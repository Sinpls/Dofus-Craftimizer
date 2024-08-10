# main.py
from pprint import pprint
from models import IngredientManager, Ingredient
from utils import process_recipe
from data_access import data_access  # Updated import
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
        self.resource_usage = {}  # To track which items use which resources
        self.non_zero_cost_items = set()  # To track items with non-zero costs
        self.total_amounts = {}  # To track total amounts of ingredients and intermediate items
        self.user_set_costs = {}  # To store user-set costs for intermediate items
        self.original_intermediate_items = {}  # To store original intermediate items data
        

        self.ui = DofusCraftimizerUI(master, self)

    def get_clean_type(self, type_data):
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
            
    def search_equipment(self, event=None):
        query = self.ui.get_search_query()
        results = data_access.search_items('dofus_equipment.json', query)

        self.ui.clear_results()
        for item in results:
            clean_type = self.get_clean_type(item['type'])
            self.ui.insert_result((item['name'], item['level'], clean_type), item['ankama_id'])


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
            return data_access.find_item_by_id(ankama_id)  # Updated function call
        except ValueError:
            # If not an integer, search by name
            item_details = data_access.search_items('dofus_equipment.json', name_or_id)  # Updated function call
            if not item_details:
                item_details = data_access.search_items('dofus_resources.json', name_or_id)  # Updated function call
            if not item_details:
                item_details = data_access.search_items('dofus_consumables.json', name_or_id)  # Updated function call
        
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
        selection = self.ui.equipment_tree.selection()
        if not selection:
            return  # Exit the method if no item is selected
        
        item = selection[0]
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
        selection = self.ui.ingredients_tree.selection()
        if not selection:
            return  # Exit the method if no item is selected
        
        item = selection[0]
        column = self.ui.ingredients_tree.identify_column(event.x)
        
        if column == "#3":  # Cost column
            entry = self.ui.create_edit_entry(self.ui.ingredients_tree, item, column)
            entry.bind("<FocusOut>", lambda e: self.update_ingredient_value(e, item, column, entry))
            entry.bind("<Return>", lambda e: self.update_ingredient_value(e, item, column, entry))


    def on_intermediate_double_click(self, event):
        selection = self.ui.intermediate_tree.selection()
        if not selection:
            return  # Exit the method if no item is selected

        item = selection[0]
        column = self.ui.intermediate_tree.identify_column(event.x)
        
        if column == "#3":  # Cost column
            entry = self.ui.create_edit_entry(self.ui.intermediate_tree, item, column)
            entry.bind("<FocusOut>", lambda e: self.update_intermediate_value(e, item, column, entry))
            entry.bind("<Return>", lambda e: self.update_intermediate_value(e, item, column, entry))


    def update_ingredient_value(self, event, item, column, entry):
        new_value = entry.get()
        try:
            cost = float(new_value)
            name = self.ui.ingredients_tree.set(item, "#1")
            
            if cost == 0 and name in self.original_intermediate_items:
                # Revert the intermediate item
                del self.user_set_costs[name]
                self.intermediate_items[name] = self.original_intermediate_items[name].copy()
            else:
                self.user_set_costs[name] = cost
                if name in self.intermediate_items:
                    del self.intermediate_items[name]
            
            ingredient = self.ingredient_manager.get_ingredient(name)
            if ingredient:
                ingredient.cost = cost
        except ValueError:
            logger.error(f"Invalid cost value entered: {new_value}")
        
        entry.destroy()
        self.calculate()
    
    def update_intermediate_value(self, event, item, column, entry):
        new_value = entry.get()
        try:
            cost = float(new_value)
            name = self.ui.intermediate_tree.set(item, "#1")
            self.user_set_costs[name] = cost
            if name in self.intermediate_items:
                self.intermediate_items[name]['cost'] = cost
            if cost > 0:
                self.non_zero_cost_items.add(name)
            else:
                self.non_zero_cost_items.discard(name)
        except ValueError:
            logger.error(f"Invalid cost value entered: {new_value}")
        
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

    def calculate_item_cost(self, item_details, amount, level, parent_item=None):
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

                        # Update total amounts
                        if ingredient_name not in self.total_amounts:
                            self.total_amounts[ingredient_name] = 0
                        self.total_amounts[ingredient_name] += ingredient_amount

                        if ingredient_name in self.user_set_costs:
                            # Use the user-set cost for items
                            ingredient_cost = self.user_set_costs[ingredient_name]
                            total_cost += ingredient_cost * ingredient_amount
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
                                # Store original data
                                self.original_intermediate_items[ingredient_name] = self.intermediate_items[ingredient_name].copy()
                        else:
                            ingredient_cost = self.user_set_costs.get(ingredient_name, self.ingredient_manager.get_ingredient_cost(ingredient_name))
                            item_cost = ingredient_amount * ingredient_cost
                            total_cost += item_cost
                            self.ingredient_manager.add_or_update_ingredient(
                                ingredient_name,
                                ingredient_amount,
                                ingredient_cost,
                                ingredient_type=ingredient_type
                            )
                        
                        # Track resource usage
                        if parent_item:
                            if ingredient_name not in self.resource_usage:
                                self.resource_usage[ingredient_name] = set()
                            self.resource_usage[ingredient_name].add(parent_item)

        return total_cost
    
    def should_hide_resource(self, resource_name):
        if resource_name not in self.resource_usage:
            return False
        return all(parent in self.non_zero_cost_items for parent in self.resource_usage[resource_name])
    
    def add_ingredients_to_hidden(self, item_details):
        if 'recipe' in item_details and item_details['recipe']:
            ingredients = process_recipe(item_details['recipe'], 1)
            for ingredient in ingredients:
                if isinstance(ingredient, dict) and 'ankama_id' in ingredient:
                    ingredient_details = self.get_item_details(ingredient['ankama_id'])
                    if ingredient_details:
                        self.hidden_resources.add(ingredient_details['name'])
                        # Recursively add sub-ingredients
                        self.add_ingredients_to_hidden(ingredient_details)
                        
    def update_ingredients_list(self):
        self.ui.clear_ingredients()
        for ingredient_name, total_amount in self.total_amounts.items():
            if ingredient_name in self.user_set_costs or ingredient_name not in self.intermediate_items:
                ingredient = self.ingredient_manager.get_ingredient(ingredient_name)
                if ingredient:
                    cost = self.user_set_costs.get(ingredient_name, ingredient.cost)
                    self.ui.insert_ingredient((
                        ingredient_name, total_amount, cost, ingredient.type
                    ))
                else:
                    # Handle case where ingredient is not in IngredientManager (e.g., intermediate items with user-set cost)
                    cost = self.user_set_costs.get(ingredient_name, 0)
                    ingredient_type = self.intermediate_items.get(ingredient_name, {}).get('type', 'Intermediate')
                    self.ui.insert_ingredient((
                        ingredient_name, total_amount, cost, ingredient_type
                    ))

    def update_intermediate_items_list(self):
        self.ui.clear_intermediate_items()
        for name, details in self.intermediate_items.items():
            if name not in self.user_set_costs:
                total_amount = self.total_amounts.get(name, 0)
                self.ui.insert_intermediate_item((
                    name, total_amount, f"{details['cost']:.2f}", details['level']
                ))

    def calculate(self):
        self.resource_usage.clear()
        self.total_amounts.clear()
        temp_intermediate_items = self.intermediate_items.copy()
        self.intermediate_items.clear()
        
        # Instead of clearing all ingredients, update their amounts to 0
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
                self.ui.set_equipment_value(item, "Cost per Unit", f"{cost_per_unit:.2f}")
                self.ui.set_equipment_value(item, "Profit", f"{profit_per_unit:.2f}")

        # Restore user-set costs and levels for intermediate items
        for name, details in temp_intermediate_items.items():
            if name in self.intermediate_items:
                self.intermediate_items[name]['level'] = details['level']
                if name in self.user_set_costs:
                    self.intermediate_items[name]['cost'] = self.user_set_costs[name]
        
        self.update_ingredients_list()
        self.update_intermediate_items_list()


    def remove_selected_equipment(self, event=None):
            selected_items = self.ui.equipment_tree.selection()
            for item in selected_items:
                self.ui.equipment_tree.delete(item)
                if item in self.equipment_data:
                    del self.equipment_data[item]
            self.calculate()
            self.update_ingredients_list()
            self.update_intermediate_items_list()
            
if __name__ == "__main__":
    root = tk.Tk()
    app = DofusCraftimizer(root)
    root.mainloop()