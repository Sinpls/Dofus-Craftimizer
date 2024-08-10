# main.py
from pprint import pprint
from models import IngredientManager, Ingredient
from utils import process_recipe
from search import search_json, get_item_details, find_resource_by_id
from functools import lru_cache
import tkinter as tk
from ui import DofusCraftimizerUI

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DofusCraftimizer:
    def __init__(self, master):
        self.master = master
        self.ingredient_manager = IngredientManager()
        self.equipment_data = {}  # To store sell prices
        self.intermediate_items = {}  # To store intermediate items

        self.ui = DofusCraftimizerUI(master, self)

    def search_equipment(self, event=None):
        query = self.ui.get_search_query()
        results = search_json('dofus_equipment.json', query)

        self.ui.clear_results()
        self.ui.populate_results(results)

    def add_to_equipment_list(self):
        selected_items = self.ui.get_selected_results()
        for selected_item in selected_items:
            values = self.ui.get_result_values(selected_item)
            ankama_id = self.ui.get_result_ankama_id(selected_item)
            
            # Check if the item already exists in the equipment list
            item_exists = False
            for item in self.ui.get_equipment_children():
                if self.ui.get_equipment_item_tags(item)[0] == ankama_id:
                    item_exists = True
                    break
            
            if not item_exists:
                item_id = self.ui.insert_equipment(ankama_id, (values[0], "1", "0", "0", "0"))
                self.equipment_data[item_id] = {"sell_price": 0}
        
        self.update_single_item()
        self.update_ingredients_list()

    @lru_cache(maxsize=100)
    def get_item_details(self, name_or_id):
        # Try to convert to int for ankama_id search
        try:
            ankama_id = int(name_or_id)
            return get_item_details(ankama_id)
        except ValueError:
            # If not an integer, search by name
            item_details = search_json('dofus_equipment.json', name_or_id)
            if not item_details:
                item_details = search_json('dofus_resources.json', name_or_id)
            if not item_details:
                item_details = search_json('dofus_consumables.json', name_or_id)
        
        return item_details[0] if item_details else None
    
    @lru_cache(maxsize=None)
    def _memoized_item_cost(self, item_id, amount):
        item_details = self.get_item_details(item_id)
        if not item_details:
            return 0

        total_cost = 0
        if 'recipe' in item_details and item_details['recipe']:
            ingredients = process_recipe(item_details['recipe'], amount)
            for ingredient in ingredients:
                if isinstance(ingredient, dict) and 'ankama_id' in ingredient:
                    ingredient_details = self.get_item_details(ingredient['ankama_id'])
                    if ingredient_details:
                        if 'recipe' in ingredient_details and ingredient_details['recipe']:
                            sub_cost = self._memoized_item_cost(ingredient['ankama_id'], ingredient['amount'])
                            total_cost += sub_cost
                            self.intermediate_items[ingredient_details['name']] = {
                                'amount': ingredient['amount'],
                                'cost': sub_cost / ingredient['amount'] if ingredient['amount'] > 0 else 0,
                                'level': 0  # We'll handle levels differently
                            }
                        else:
                            ingredient_cost = self.ingredient_manager.get_ingredient_cost(ingredient_details['name'])
                            item_cost = ingredient['amount'] * ingredient_cost
                            total_cost += item_cost
                            self.ingredient_manager.add_or_update_ingredient(
                                ingredient_details['name'],
                                ingredient['amount'],
                                ingredient_cost,
                                ingredient_type=ingredient_details.get('type', 'unknown')
                            )
        return total_cost
    def on_equipment_double_click(self, event):
        item = self.ui.equipment_tree.selection()[0]
        column = self.ui.equipment_tree.identify_column(event.x)
        
        if column in ("#2", "#4"):  # Amount or Sell Price column
            entry = self.ui.create_edit_entry(self.ui.equipment_tree, item, column)
            entry.bind("<FocusOut>", lambda e: self.update_equipment_value(e, item, column, entry))
            entry.bind("<Return>", lambda e: self.update_equipment_value(e, item, column, entry))

    def update_equipment_value(self, event, item, column, entry):
        new_value = entry.get()
        self.ui.set_equipment_value(item, column, new_value)
        if column == "#4":  # Sell Price column
            self.equipment_data[item]["sell_price"] = float(new_value)
        entry.destroy()
        self.update_single_item(item)

    def on_ingredient_double_click(self, event):
        item = self.ui.ingredients_tree.selection()[0]
        column = self.ui.ingredients_tree.identify_column(event.x)
        
        if column == "#3":  # Cost column
            entry = self.ui.create_edit_entry(self.ui.ingredients_tree, item, column)
            entry.bind("<FocusOut>", lambda e: self.update_ingredient_value(e, item, column, entry))
            entry.bind("<Return>", lambda e: self.update_ingredient_value(e, item, column, entry))

    def on_intermediate_double_click(self, event):
        item = self.ui.intermediate_tree.selection()[0]
        column = self.ui.intermediate_tree.identify_column(event.x)
        
        if column == "#3":  # Cost column
            entry = self.ui.create_edit_entry(self.ui.intermediate_tree, item, column)
            entry.bind("<FocusOut>", lambda e: self.update_intermediate_value(e, item, column, entry))
            entry.bind("<Return>", lambda e: self.update_intermediate_value(e, item, column, entry))

    def update_ingredient_value(self, event, item, column, entry):
        new_value = entry.get()
        self.ui.ingredients_tree.set(item, column, new_value)
        ingredient_name = self.ui.ingredients_tree.set(item, "#1")
        self.ingredient_manager.update_ingredient_cost(ingredient_name, float(new_value))
        entry.destroy()
        self.calculate()
    
    def update_intermediate_value(self, event, item, column, entry):
        new_value = entry.get()
        self.ui.intermediate_tree.set(item, column, new_value)
        intermediate_name = self.ui.intermediate_tree.set(item, "#1")
        self.intermediate_items[intermediate_name]['cost'] = float(new_value)
        entry.destroy()
        self.calculate()

    def update_single_item(self):
        for item in self.ui.get_equipment_children():
            name = self.ui.get_equipment_value(item, "Name")
            amount = int(self.ui.get_equipment_value(item, "Amount"))
            sell_price = float(self.equipment_data[item]["sell_price"])

            item_details = self.get_item_details(name)
            if item_details:
                cost_per_unit = self.calculate_item_cost(item_details, 1, 1) / 1  # Calculate for 1 unit
                
                total_cost = cost_per_unit * amount
                total_sell = sell_price * amount
                profit = total_sell - total_cost
                
                self.ui.set_equipment_value(item, "Cost per Unit", f"{cost_per_unit:.2f}")
                self.ui.set_equipment_value(item, "Profit", f"{profit:.2f}")

                # Color coding
                if sell_price != 0:
                    if profit > 0:
                        self.ui.set_equipment_tags(item, ('profit',))
                    elif profit < 0:
                        self.ui.set_equipment_tags(item, ('loss',))
                    else:
                        self.ui.set_equipment_tags(item, ())

        self.update_ingredients_list()
        self.update_intermediate_items_list()

    def calculate_item_cost(self, item_details, amount, level):
        self.intermediate_items.clear()  # Clear previous intermediate items
        total_cost = self._memoized_item_cost(item_details['ankama_id'], amount)
        
        # Update levels for intermediate items
        for name, details in self.intermediate_items.items():
            details['level'] = level
        
        return total_cost
    
    def update_ingredients_list(self):
        self.ui.clear_ingredients()
        for ingredient in self.ingredient_manager.get_ingredients_list():
            if ingredient.amount > 0:  # Only show ingredients with amount > 0
                self.ui.insert_ingredient((
                    ingredient.name, ingredient.amount, ingredient.cost, ingredient.type
                ))

    def update_intermediate_items_list(self):
        self.ui.clear_intermediate_items()
        for name, details in self.intermediate_items.items():
            self.ui.insert_intermediate_item((
                name, details['amount'], f"{details['cost']:.2f}", details['level']
            ))

    def calculate(self):
        for item in self.ui.get_equipment_children():
            name = self.ui.get_equipment_value(item, "Name")
            amount = int(self.ui.get_equipment_value(item, "Amount"))
            sell_price = float(self.equipment_data[item]["sell_price"])

            item_details = self.get_item_details(name)
            if item_details and item_details.get('recipe'):
                cost_per_unit = self.calculate_item_cost(item_details, 1, 1) / 1  # Calculate for 1 unit
                
                profit_per_unit = sell_price - cost_per_unit
                self.ui.set_equipment_value(item, "Cost per Unit", f"{cost_per_unit:.2f}")
                self.ui.set_equipment_value(item, "Profit", f"{profit_per_unit:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DofusCraftimizer(root)
    root.mainloop()