# main.py
from pprint import pprint
import tkinter as tk
from tkinter import ttk
from ingredient_manager import IngredientManager, Ingredient, process_recipe
from search import search_json, find_resource_by_id
from functools import lru_cache

class DofusCraftimizer:
    def __init__(self, master):
        self.master = master
        self.master.title("Dofus Craftimizer")
        self.master.geometry("1600x1000")  # Adjusted width since we removed a column

        self.ingredient_manager = IngredientManager()
        self.equipment_data = {}  # To store sell prices

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Search frame
        search_frame = ttk.Frame(main_frame, padding="5")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        search_frame.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        search_entry.bind("<Return>", self.search_equipment)  # Bind Enter key to search function


        # Results and Equipment frame
        results_equipment_frame = ttk.Frame(main_frame, padding="5")
        results_equipment_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_equipment_frame.columnconfigure(0, weight=1)
        results_equipment_frame.columnconfigure(1, weight=1)
        results_equipment_frame.rowconfigure(0, weight=1)

        # Search results frame
        results_frame = ttk.LabelFrame(results_equipment_frame, text="Search Results", padding="5")
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.results_tree = ttk.Treeview(results_frame, columns=("Name", "Level", "Type"), show="headings")
        self.results_tree.heading("Name", text="Name")
        self.results_tree.heading("Level", text="Level")
        self.results_tree.heading("Type", text="Type")
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        add_button = ttk.Button(results_frame, text="Add to Equipment List", command=self.add_to_equipment_list)
        add_button.grid(row=1, column=0, pady=(5, 0))

        # Equipment list frame
        equipment_frame = ttk.LabelFrame(results_equipment_frame, text="Equipment List", padding="5")
        equipment_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        equipment_frame.columnconfigure(0, weight=1)
        equipment_frame.rowconfigure(0, weight=1)

        self.equipment_tree = ttk.Treeview(equipment_frame, columns=("Name", "Amount", "Cost per Unit", "Sell Price", "Profit"), show="headings")
        self.equipment_tree.heading("Name", text="Name")
        self.equipment_tree.heading("Amount", text="Amount")
        self.equipment_tree.heading("Cost per Unit", text="Cost per Unit")
        self.equipment_tree.heading("Sell Price", text="Sell Price")
        self.equipment_tree.heading("Profit", text="Profit")
        self.equipment_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Ingredients list frame
        ingredients_frame = ttk.LabelFrame(main_frame, text="Ingredients List", padding="5")
        ingredients_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        ingredients_frame.columnconfigure(0, weight=1)
        ingredients_frame.rowconfigure(0, weight=1)

        self.ingredients_tree = ttk.Treeview(ingredients_frame, columns=("Name", "Amount", "Cost", "Type"), show="headings")
        self.ingredients_tree.heading("Name", text="Name")
        self.ingredients_tree.heading("Amount", text="Amount")
        self.ingredients_tree.heading("Cost", text="Cost")
        self.ingredients_tree.heading("Type", text="Type")
        self.ingredients_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ingredients_scrollbar = ttk.Scrollbar(ingredients_frame, orient="vertical", command=self.ingredients_tree.yview)
        ingredients_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.ingredients_tree.configure(yscrollcommand=ingredients_scrollbar.set)

        self.ingredients_tree.bind("<Double-1>", self.on_ingredient_double_click)

        # Define tags for color coding
        self.equipment_tree.tag_configure('profit', background='light green')
        self.equipment_tree.tag_configure('loss', background='light coral')

        equipment_scrollbar = ttk.Scrollbar(equipment_frame, orient="vertical", command=self.equipment_tree.yview)
        equipment_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.equipment_tree.configure(yscrollcommand=equipment_scrollbar.set)

        self.equipment_tree.bind("<Double-1>", self.on_equipment_double_click)

    def search_equipment(self, event=None):  # Added event parameter for key binding
        query = self.search_var.get()
        results = search_json('dofus_equipment.json', query)

        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Populate results
        for item in results:
            self.results_tree.insert("", "end", values=(item['name'], item['level'], item['type']), tags=(item['ankama_id'],))

    def add_to_equipment_list(self):
        selected_items = self.results_tree.selection()
        for selected_item in selected_items:
            values = self.results_tree.item(selected_item)['values']
            ankama_id = self.results_tree.item(selected_item)['tags'][0]
            
            # Check if the item already exists in the equipment list
            item_exists = False
            for item in self.equipment_tree.get_children():
                if self.equipment_tree.item(item)['tags'][0] == ankama_id:
                    item_exists = True
                    break
            
            if not item_exists:
                item_id = self.equipment_tree.insert("", "end", values=(values[0], "1", "0", "0", "0"), tags=(ankama_id,))
                self.equipment_data[item_id] = {"sell_price": 0}
                self.update_single_item(item_id)
        
        self.update_ingredients_list()

    def on_equipment_double_click(self, event):
        item = self.equipment_tree.selection()[0]
        column = self.equipment_tree.identify_column(event.x)
        
        if column in ("#2", "#4"):  # Amount or Sell Price column
            x, y, width, height = self.equipment_tree.bbox(item, column)
            
            value = self.equipment_tree.set(item, column)
            
            entry = ttk.Entry(self.equipment_tree, width=width//8)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, value)
            entry.select_range(0, tk.END)
            entry.focus()
            
            entry.bind("<FocusOut>", lambda e: self.update_equipment_value(e, item, column, entry))
            entry.bind("<Return>", lambda e: self.update_equipment_value(e, item, column, entry))

    @lru_cache(maxsize=100)
    def get_item_details(self, name):
        item_details = search_json('dofus_equipment.json', name)
        if item_details and item_details[0]['recipe']:
            return item_details[0]
        return None
    
    def update_equipment_value(self, event, item, column, entry):
        new_value = entry.get()
        self.equipment_tree.set(item, column, new_value)
        if column == "#4":  # Sell Price column
            self.equipment_data[item]["sell_price"] = float(new_value)
        entry.destroy()
        self.update_single_item(item)

    def on_ingredient_double_click(self, event):
        item = self.ingredients_tree.selection()[0]
        column = self.ingredients_tree.identify_column(event.x)
        
        if column == "#3":  # Cost column
            x, y, width, height = self.ingredients_tree.bbox(item, column)
            
            value = self.ingredients_tree.set(item, column)
            
            entry = ttk.Entry(self.ingredients_tree, width=width//8)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, value)
            entry.select_range(0, tk.END)
            entry.focus()
            
            entry.bind("<FocusOut>", lambda e: self.update_ingredient_value(e, item, column, entry))
            entry.bind("<Return>", lambda e: self.update_ingredient_value(e, item, column, entry))

    def update_ingredient_value(self, event, item, column, entry):
        new_value = entry.get()
        self.ingredients_tree.set(item, column, new_value)
        ingredient_name = self.ingredients_tree.set(item, "#1")
        self.ingredient_manager.update_ingredient_cost(ingredient_name, float(new_value))
        entry.destroy()
        self.calculate()

    def update_single_item(self, item):
        name = self.equipment_tree.set(item, "Name")
        amount = int(self.equipment_tree.set(item, "Amount"))
        sell_price = float(self.equipment_data[item]["sell_price"])

        item_details = self.get_item_details(name)
        if item_details:
            ingredients = process_recipe(item_details['recipe'], 1)  # Calculate for 1 unit
            cost_per_unit = sum(
                self.ingredient_manager.get_ingredient_cost(find_resource_by_id(ingredient['ankama_id'])) * ingredient['amount']
                for ingredient in ingredients
                if isinstance(ingredient, dict) and 'ankama_id' in ingredient
            )
            
            profit_per_unit = sell_price - cost_per_unit
            self.equipment_tree.set(item, "Cost per Unit", f"{cost_per_unit:.2f}")
            self.equipment_tree.set(item, "Profit", f"{profit_per_unit:.2f}")

            # Color coding
            if sell_price != 0:
                if profit_per_unit > cost_per_unit:
                    self.equipment_tree.item(item, tags=('profit',))
                elif profit_per_unit < cost_per_unit:
                    self.equipment_tree.item(item, tags=('loss',))
                else:
                    self.equipment_tree.item(item, tags=())

        self.update_ingredients_list()

    def update_ingredients_list(self):
        self.ingredient_manager.clear_amounts()

        for item in self.equipment_tree.get_children():
            name = self.equipment_tree.set(item, "Name")
            amount = int(self.equipment_tree.set(item, "Amount"))

            item_details = self.get_item_details(name)
            if item_details:
                ingredients = process_recipe(item_details['recipe'], amount)
                for ingredient in ingredients:
                    if isinstance(ingredient, dict) and 'ankama_id' in ingredient:
                        ingredient_name = find_resource_by_id(ingredient['ankama_id'])
                        if ingredient_name:
                            current_amount = self.ingredient_manager.ingredients.get(ingredient_name, Ingredient(ingredient_name)).amount
                            new_amount = current_amount + ingredient['amount']
                            self.ingredient_manager.add_or_update_ingredient(
                                ingredient_name,
                                new_amount,
                                ingredient_type=ingredient.get('type', 'unknown')
                            )
                        else:
                            print(f"Unknown resource with ID: {ingredient['ankama_id']}")
                    else:
                        print(f"Invalid ingredient data: {ingredient}")

        self.refresh_ingredients_tree()

    def refresh_ingredients_tree(self):
        for item in self.ingredients_tree.get_children():
            self.ingredients_tree.delete(item)

        for ingredient in self.ingredient_manager.get_ingredients_list():
            if ingredient.amount > 0:  # Only show ingredients with amount > 0
                self.ingredients_tree.insert("", "end", values=(
                    ingredient.name, ingredient.amount, ingredient.cost, ingredient.type
                ))

    def calculate(self):
        for item in self.equipment_tree.get_children():
            name = self.equipment_tree.set(item, "Name")
            amount = int(self.equipment_tree.set(item, "Amount"))
            sell_price = float(self.equipment_data[item]["sell_price"])

            item_details = search_json('dofus_equipment.json', name)
            if item_details and item_details[0]['recipe']:
                ingredients = process_recipe(item_details[0]['recipe'], 1)  # Calculate for 1 unit
                cost_per_unit = 0
                for ingredient in ingredients:
                    if isinstance(ingredient, dict) and 'ankama_id' in ingredient:
                        ingredient_name = find_resource_by_id(ingredient['ankama_id'])
                        if ingredient_name:
                            ingredient_cost = self.ingredient_manager.get_ingredient_cost(ingredient_name)
                            cost_per_unit += ingredient['amount'] * ingredient_cost
                
                profit_per_unit = sell_price - cost_per_unit
                self.equipment_tree.set(item, "Cost per Unit", f"{cost_per_unit:.2f}")
                self.equipment_tree.set(item, "Profit", f"{profit_per_unit:.2f}")
    
    def color_code_equipment_rows(self):
        for item in self.equipment_tree.get_children():
            cost_per_unit = float(self.equipment_tree.set(item, "Cost per Unit"))
            sell_price = float(self.equipment_data[item]["sell_price"])
            profit = float(self.equipment_tree.set(item, "Profit"))

            if sell_price != 0:
                if profit > cost_per_unit:
                    self.equipment_tree.item(item, tags=('profit',))
                elif profit < cost_per_unit:
                    self.equipment_tree.item(item, tags=('loss',))
                else:
                    self.equipment_tree.item(item, tags=())

if __name__ == "__main__":
    root = tk.Tk()
    app = DofusCraftimizer(root)
    root.mainloop()