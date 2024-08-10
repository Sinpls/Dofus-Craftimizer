# main.py
import logging
from functools import lru_cache
import tkinter as tk
from typing import Dict, Any

from pprint import pprint
from models import IngredientManager, Ingredient
from utils import process_recipe
from data_access import data_access
from ui import DofusCraftimizerUI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DofusCraftimizer:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.ingredient_manager = IngredientManager()
        self.equipment_data: Dict[str, Dict[str, float]] = {}
        self.intermediate_items: Dict[str, Dict[str, Any]] = {}
        self.resource_usage: Dict[str, set] = {}
        self.non_zero_cost_items: set = set()
        self.total_amounts: Dict[str, int] = {}
        self.user_set_costs: Dict[str, float] = {}
        self.original_intermediate_items: Dict[str, Dict[str, Any]] = {}

        self.ui = DofusCraftimizerUI(master, self)

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
                tags = self.ui.get_equipment_item_tags(item)
                if tags and tags[0] == ankama_id:
                    item_exists = True
                    break
            
            if not item_exists:
                item_id = self.ui.insert_equipment(ankama_id, (values[0], "1", "0", "0", "0"))
                self.equipment_data[item_id] = {"sell_price": 0, "amount": 1}
        
        self.update_single_item()
        self.update_ingredients_list()

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

    def calculate_item_cost(self, item_details: Dict[str, Any], amount: int, level: int, parent_item: str = None) -> float:
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
    
    def update_item(self, tree, item, column, new_value):
        tree_id = str(tree)
        if tree_id == str(self.ui.equipment_tree):
            if column == "#2":  # Amount
                self.equipment_data[item] = self.equipment_data.get(item, {})
                self.equipment_data[item]["amount"] = int(new_value)
            elif column == "#4":  # Sell Price
                self.equipment_data[item] = self.equipment_data.get(item, {})
                self.equipment_data[item]["sell_price"] = float(new_value)
            self.update_single_item()
        elif tree_id == str(self.ui.ingredients_tree):
            ingredient_name = self.ui.get_tree_item_values(tree, item)[0]
            self.user_set_costs[ingredient_name] = float(new_value)
        elif tree_id == str(self.ui.intermediate_tree):
            item_name = self.ui.get_tree_item_values(tree, item)[0]
            self.user_set_costs[item_name] = float(new_value)
            if item_name in self.intermediate_items:
                self.intermediate_items[item_name]['cost'] = float(new_value)
        
        self.calculate()

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
                
                self.ui.set_equipment_value(item, "Cost per Unit", f"{cost_per_unit:.2f}")
                self.ui.set_equipment_value(item, "Profit", f"{profit:.2f}")

                # Color coding
                self.ui.set_equipment_tags(item, ('profit',) if profit > 0 else ('loss',) if profit < 0 else ())

        self.update_ingredients_list()
        self.update_intermediate_items_list()

    def update_ingredients_list(self):
        self.ui.clear_ingredients()
        for ingredient_name, total_amount in self.total_amounts.items():
            if ingredient_name in self.user_set_costs or ingredient_name not in self.intermediate_items:
                ingredient = self.ingredient_manager.get_ingredient(ingredient_name)
                cost = self.user_set_costs.get(ingredient_name, ingredient.cost if ingredient else 0)
                ingredient_type = ingredient.type if ingredient else self.intermediate_items.get(ingredient_name, {}).get('type', 'Intermediate')
                self.ui.insert_ingredient((ingredient_name, total_amount, cost, ingredient_type))

    def update_intermediate_items_list(self):
        self.ui.clear_intermediate_items()
        for name, details in self.intermediate_items.items():
            if name not in self.user_set_costs:
                total_amount = self.total_amounts.get(name, 0)
                self.ui.insert_intermediate_item((name, total_amount, f"{details['cost']:.2f}", details['level']))

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
                self.ui.set_equipment_value(item, "Cost per Unit", f"{cost_per_unit:.2f}")
                self.ui.set_equipment_value(item, "Profit", f"{profit_per_unit:.2f}")

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
            self.equipment_data.pop(item, None)
        self.calculate()
        self.update_ingredients_list()
        self.update_intermediate_items_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = DofusCraftimizer(root)
    root.mainloop()