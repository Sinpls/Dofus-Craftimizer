import os
import sys
from contextlib import contextmanager
import logging
import json
from functools import lru_cache
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
import threading

from models import IngredientManager
from utils import process_recipe
from data_access import data_access
from ui import StyledDofusCraftimizerUI
from api_importer import update_dofus_data, check_files_exist, get_data_dir

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@contextmanager
def loading_screen(master):
    screen = LoadingScreen(master)
    screen.start()
    try:
        yield screen
    finally:
        screen.stop()
        screen.destroy()

class LoadingScreen:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.progress = ttk.Progressbar(self.frame, length=300, mode='indeterminate')
        self.progress.pack(pady=20)

        self.status_label = ttk.Label(self.frame, text="Loading...")
        self.status_label.pack()

        self.is_destroyed = False

    def start(self):
        if not self.is_destroyed:
            self.progress.start()

    def stop(self):
        if not self.is_destroyed:
            self.progress.stop()

    def update_status(self, message):
        if not self.is_destroyed:
            self.status_label.config(text=message)

    def destroy(self):
        if not self.is_destroyed:
            self.is_destroyed = True
            self.frame.destroy()
    
class DofusCraftimizer:
    def __init__(self, master: tk.Tk):
        logger.info("Initializing DofusCraftimizer")
        self.master = master
        self.master.title("Dofus Craftimizer")
        
        # Set an initial size
        self.master.geometry("800x600")

        # Allow the window to be resized
        self.master.resizable(True, True)

        self.ingredient_manager = IngredientManager()
        self.equipment_data: Dict[str, Dict[str, float]] = {}
        self.intermediate_items: Dict[str, Dict[str, Any]] = {}
        self.resource_usage: Dict[str, set] = {}
        self.total_amounts: Dict[str, int] = {}
        self.user_set_costs: Dict[str, float] = {}
        self.original_intermediate_items: Dict[str, Dict[str, Any]] = {}

        self.loading_screen = None
        self.center_window(self.master)
        self.initialize_app()

    def initialize_app(self):
        logger.info("Starting initialization process")
        if not check_files_exist():
            logger.info("JSON files not found, starting download")
            self.show_loading_screen("Downloading data files...")
            self.start_update()
        else:
            logger.info("JSON files found, loading main UI")
            self.load_main_ui()

    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def show_loading_screen(self, message):
        if self.loading_screen is None:
            self.loading_screen = LoadingScreen(self.master)
        self.loading_screen.update_status(message)

    def hide_loading_screen(self):
        if self.loading_screen:
            self.loading_screen.stop()
            self.loading_screen.destroy()
            self.loading_screen = None

    def start_update(self):
        self.update_thread = threading.Thread(target=self.update_data)
        self.update_thread.start()
        self.master.after(100, self.check_update_complete)

    def update_data(self):
        logger.info("Updating Dofus data (calling api_importer)")
        try:
            update_dofus_data(self.update_status)
        except Exception as e:
            logger.error(f"Error updating Dofus data: {e}")
            self.master.after(0, self.show_error_message, f"Failed to update data: {e}\nThe application may not function correctly.")
        else:
            logger.info("Data update complete")

    def update_status(self, message):
        if self.loading_screen:
            self.master.after(0, self.loading_screen.update_status, message)

    def check_update_complete(self):
        if self.update_thread.is_alive():
            self.master.after(100, self.check_update_complete)
        else:
            logger.info("Update complete, loading main UI")
            self.hide_loading_screen()
            self.load_main_ui()

    def show_error_message(self, message):
        self.hide_loading_screen()
        messagebox.showerror("Error", message)
        self.master.quit()

    def load_main_ui(self):
        try:
            self.ui = StyledDofusCraftimizerUI(self.master, self)
            logger.info("Main UI created and displayed")
            
            # Adjust window size after main UI is loaded
            self.master.update_idletasks()
            width = max(800, self.master.winfo_reqwidth())
            height = max(600, self.master.winfo_reqheight())
            self.master.geometry(f"{width}x{height}")
            self.center_window(self.master)
        except Exception as e:
            logger.error(f"Error loading main UI: {e}")
            self.show_error_message(f"Failed to load main UI: {e}")
    
    def search_equipment(self, event=None):
        query = self.ui.get_search_query()
        results = data_access.search_items('dofus_equipment.json', query)

        self.ui.clear_results()
        for item in results:
            clean_type = self.get_clean_type(item['type'])
            self.ui.insert_result((item['name'], item['level'], clean_type), item['ankama_id'])

    def add_to_equipment_list(self, event=None):
        if event:  # If triggered by double-click
            selected_items = [self.ui.results_tree.focus()]
        else:  # If called programmatically
            selected_items = self.ui.get_selected_results()

        for selected_item in selected_items:
            values = self.ui.get_result_values(selected_item)
            item_name = values[0]  # Assuming the first value is the item name
            
            # Check if the item already exists in the equipment list
            existing_item = None
            for item in self.ui.get_equipment_children():
                if self.ui.get_equipment_value(item, "Name") == item_name:
                    existing_item = item
                    break
            
            if existing_item:
                # If the item exists, increase its amount by 1
                current_amount = int(self.ui.get_equipment_value(existing_item, "Amount"))
                new_amount = current_amount + 1
                self.ui.set_equipment_value(existing_item, "Amount", str(new_amount))
                self.equipment_data[existing_item]["amount"] = new_amount
            else:
                # If the item doesn't exist, add it to the list
                item_id = self.ui.insert_equipment(item_name, (item_name, "1", "0", "0", "0"))
                self.equipment_data[item_id] = {"sell_price": 0, "amount": 1}
        
        self.update_single_item()
        self.update_ingredients_list()
        self.ui.deselect_all_trees()  # Deselect all after adding

    def remove_selected_equipment(self, event=None):
        selected_items = self.ui.equipment_tree.selection()
        for item in selected_items:
            self.ui.equipment_tree.delete(item)
            self.equipment_data.pop(item, None)
        self.calculate()
        self.update_ingredients_list()
        self.update_intermediate_items_list()
        self.ui.deselect_all_trees()  # Deselect all after removing

    def update_item(self, tree, item, column, new_value):
        tree_id = str(tree)
        if tree_id == str(self.ui.equipment_tree):
            if column == "#2":  # Amount
                self.equipment_data[item] = self.equipment_data.get(item, {})
                self.equipment_data[item]["amount"] = self.parse_number(new_value)
            elif column == "#4":  # Sell Price
                self.equipment_data[item] = self.equipment_data.get(item, {})
                self.equipment_data[item]["sell_price"] = float(self.parse_number(new_value))
            self.update_single_item()
        elif tree_id == str(self.ui.ingredients_tree):
            ingredient_name = self.ui.get_tree_item_values(tree, item)[0]
            new_cost = float(self.parse_number(new_value))
            self.user_set_costs[ingredient_name] = new_cost
            if new_cost == 0 and ingredient_name in self.original_intermediate_items:
                self.move_item_to_intermediate(ingredient_name)
        elif tree_id == str(self.ui.intermediate_tree):
            item_name = self.ui.get_tree_item_values(tree, item)[0]
            new_cost = float(self.parse_number(new_value))
            self.user_set_costs[item_name] = new_cost
            if item_name in self.intermediate_items:
                self.intermediate_items[item_name]['cost'] = new_cost
            if new_cost > 0:
                self.move_item_to_ingredients(item_name)

        self.calculate()
        self.ui.deselect_all_trees()  # Deselect all after updating

    def get_clean_type(self, type_data: Any) -> str:
        if isinstance(type_data, str):
            return type_data
        elif isinstance(type_data, dict):
            return type_data.get('name', 'Unknown')
        else:
            try:
                type_dict = json.loads(type_data.replace("'", '"'))
                return type_dict.get('name', 'Unknown')
            except json.JSONDecodeError:
                return str(type_data)

    @lru_cache(maxsize=100)
    def get_item_details(self, name_or_id: str) -> Dict[str, Any]:
        try:
            ankama_id = int(name_or_id)
            return data_access.find_item_by_id(ankama_id)
        except ValueError:
            for item_type in ['dofus_equipment.json', 'dofus_resources.json', 'dofus_consumables.json']:
                item_details = data_access.search_items(item_type, name_or_id)
                if item_details:
                    return item_details[0]
        return None

    def move_item_to_ingredients(self, item_name):
        if item_name in self.intermediate_items:
            item_details = self.intermediate_items.pop(item_name)
            self.ingredient_manager.add_or_update_ingredient(
                item_name,
                self.total_amounts.get(item_name, 0),
                self.user_set_costs.get(item_name, item_details['cost']),
                ingredient_type=item_details['type']
            )
            self.update_ingredients_list()
            self.update_intermediate_items_list()

    def move_item_to_intermediate(self, item_name):
        if item_name in self.original_intermediate_items:
            original_details = self.original_intermediate_items[item_name]
            self.intermediate_items[item_name] = original_details.copy()
            self.intermediate_items[item_name]['amount'] = self.total_amounts.get(item_name, 0)
            self.ingredient_manager.remove_ingredient(item_name)
            self.user_set_costs.pop(item_name, None)
            self.update_ingredients_list()
            self.update_intermediate_items_list()

    def calculate_item_cost(self, item_details: Dict[str, Any], amount: int, level: int, parent_item: str = None) -> float:
        item_name = item_details['name']
        if item_name in self.user_set_costs:
            return self.user_set_costs[item_name] * amount

        total_cost = 0
        if 'recipe' in item_details and item_details['recipe']:
            ingredients = process_recipe(item_details['recipe'], amount)
            for ingredient in ingredients:
                if isinstance(ingredient, dict) and 'ankama_id' in ingredient:
                    ingredient_details = self.get_item_details(ingredient['ankama_id'])
                    if ingredient_details:
                        ingredient_name = ingredient_details['name']
                        ingredient_amount = ingredient['amount']
                        ingredient_type = self.get_clean_type(ingredient_details.get('type', 'Unknown'))

                        self.total_amounts[ingredient_name] = self.total_amounts.get(ingredient_name, 0) + ingredient_amount

                        if ingredient_name in self.user_set_costs:
                            total_cost += self.user_set_costs[ingredient_name] * ingredient_amount
                        elif 'recipe' in ingredient_details and ingredient_details['recipe']:
                            sub_cost = self.calculate_item_cost(ingredient_details, ingredient_amount, level + 1, parent_item or item_details['name'])
                            total_cost += sub_cost
                            if ingredient_name not in self.intermediate_items:
                                self.intermediate_items[ingredient_name] = {
                                    'amount': ingredient_amount,
                                    'cost': sub_cost / ingredient_amount if ingredient_amount > 0 else 0,
                                    'level': level + 1,
                                    'type': ingredient_type
                                }
                                self.original_intermediate_items[ingredient_name] = self.intermediate_items[ingredient_name].copy()
                        else:
                            ingredient_cost = self.user_set_costs.get(ingredient_name, self.ingredient_manager.get_ingredient_cost(ingredient_name))
                            total_cost += ingredient_amount * ingredient_cost
                            self.ingredient_manager.add_or_update_ingredient(
                                ingredient_name,
                                ingredient_amount,
                                ingredient_cost,
                                ingredient_type=ingredient_type
                            )
                        
                        if parent_item:
                            self.resource_usage.setdefault(ingredient_name, set()).add(parent_item)

        return total_cost

    def calculate(self):
        self.resource_usage.clear()
        self.total_amounts.clear()
        temp_intermediate_items = self.intermediate_items.copy()
        self.intermediate_items.clear()
        
        for ingredient in self.ingredient_manager.get_ingredients_list():
            self.ingredient_manager.update_ingredient_amount(ingredient.name, 0)

        for item in self.ui.get_equipment_children():
            name = self.ui.get_equipment_value(item, "Name")
            amount = int(self.ui.get_equipment_value(item, "Amount"))
            sell_price = float(self.equipment_data[item]["sell_price"])

            item_details = self.get_item_details(name)
            if item_details and item_details.get('recipe'):
                cost_per_unit = self.calculate_item_cost(item_details, amount, 1, name) / amount
                
                profit_per_unit = sell_price - cost_per_unit
                self.ui.set_equipment_value(item, "Cost per Unit", self.format_number(int(cost_per_unit)))
                self.ui.set_equipment_value(item, "Profit", self.format_number(int(profit_per_unit * amount)))
                
                # Update row color
                self.ui.update_equipment_row_color(item)

        for name, details in temp_intermediate_items.items():
            if name in self.intermediate_items:
                self.intermediate_items[name]['level'] = details['level']
                if name in self.user_set_costs:
                    self.intermediate_items[name]['cost'] = self.user_set_costs[name]
                else:
                    self.intermediate_items[name]['cost'] = details['cost']
        
        self.update_ingredients_list()
        self.update_intermediate_items_list()
        
    def update_single_item(self):
        for item in self.ui.get_equipment_children():
            name = self.ui.get_equipment_value(item, "Name")
            amount = int(self.ui.get_equipment_value(item, "Amount"))
            sell_price = float(self.equipment_data[item]["sell_price"])

            item_details = self.get_item_details(name)
            if item_details:
                cost_per_unit = self.calculate_item_cost(item_details, 1, 1) / 1
                
                total_cost = cost_per_unit * amount
                total_sell = sell_price * amount
                profit = total_sell - total_cost
                
                self.ui.set_equipment_value(item, "Cost per Unit", self.format_number(int(cost_per_unit)))
                self.ui.set_equipment_value(item, "Profit", self.format_number(int(profit)))

                # Update row color
                self.ui.update_equipment_row_color(item)

        self.update_ingredients_list()
        self.update_intermediate_items_list()

    def update_ingredients_list(self):
        self.ui.clear_ingredients()
        for ingredient_name, total_amount in self.total_amounts.items():
            if ingredient_name in self.user_set_costs or ingredient_name not in self.intermediate_items:
                ingredient = self.ingredient_manager.get_ingredient(ingredient_name)
                cost = self.user_set_costs.get(ingredient_name, ingredient.cost if ingredient else 0)
                ingredient_type = ingredient.type if ingredient else self.intermediate_items.get(ingredient_name, {}).get('type', 'Intermediate')
                
                # Check if it's an intermediate item
                if ingredient_name in self.original_intermediate_items:
                    ingredient_type = 'Intermediate'
                
                self.ui.insert_ingredient((ingredient_name, self.format_number(total_amount), self.format_number(int(cost)), ingredient_type))
                
    def update_intermediate_items_list(self):
        self.ui.clear_intermediate_items()
        sorted_items = sorted(self.intermediate_items.items(), key=lambda x: x[1]['level'])
        for name, details in sorted_items:
            if name not in self.user_set_costs:
                total_amount = self.total_amounts.get(name, 0)
                self.ui.insert_intermediate_item((name, self.format_number(total_amount), self.format_number(int(details['cost'])), details['level']))

    def format_number(self, number):
        return f"{number:,}"

    def parse_number(self, string):
        try:
            return int(string.replace(',', ''))
        except ValueError:
            return 0

if __name__ == "__main__":
    root = tk.Tk()
    app = DofusCraftimizer(root)
    root.mainloop()