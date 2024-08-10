import tkinter as tk
from tkinter import ttk

class DofusCraftimizerUI:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.master.title("Dofus Craftimizer")
        self.master.geometry("1600x1000")

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
        search_entry.bind("<Return>", self.controller.search_equipment)

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

        add_button = ttk.Button(results_frame, text="Add to Equipment List", command=self.controller.add_to_equipment_list)
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

        # Ingredients and Intermediate Items frame
        ingredients_intermediate_frame = ttk.Frame(main_frame, padding="5")
        ingredients_intermediate_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        ingredients_intermediate_frame.columnconfigure(0, weight=1)
        ingredients_intermediate_frame.columnconfigure(1, weight=1)
        ingredients_intermediate_frame.rowconfigure(0, weight=1)

        # Intermediate items frame
        intermediate_frame = ttk.LabelFrame(ingredients_intermediate_frame, text="Intermediate Items", padding="5")
        intermediate_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        intermediate_frame.columnconfigure(0, weight=1)
        intermediate_frame.rowconfigure(0, weight=1)

        self.intermediate_tree = ttk.Treeview(intermediate_frame, columns=("Name", "Amount", "Cost", "Level"), show="headings")
        self.intermediate_tree.heading("Name", text="Name")
        self.intermediate_tree.heading("Amount", text="Amount")
        self.intermediate_tree.heading("Cost", text="Cost")
        self.intermediate_tree.heading("Level", text="Level")
        self.intermediate_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        intermediate_scrollbar = ttk.Scrollbar(intermediate_frame, orient="vertical", command=self.intermediate_tree.yview)
        intermediate_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.intermediate_tree.configure(yscrollcommand=intermediate_scrollbar.set)

        # Ingredients list frame
        ingredients_frame = ttk.LabelFrame(ingredients_intermediate_frame, text="Ingredients List", padding="5")
        ingredients_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
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

        # Define tags for color coding
        self.equipment_tree.tag_configure('profit', background='light green')
        self.equipment_tree.tag_configure('loss', background='light coral')

        equipment_scrollbar = ttk.Scrollbar(equipment_frame, orient="vertical", command=self.equipment_tree.yview)
        equipment_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.equipment_tree.configure(yscrollcommand=equipment_scrollbar.set)

        self.equipment_tree.bind("<Double-1>", self.controller.on_equipment_double_click)
        self.ingredients_tree.bind("<Double-1>", self.controller.on_ingredient_double_click)
        self.intermediate_tree.bind("<Double-1>", self.controller.on_intermediate_double_click)

        self.equipment_tree.bind("<Delete>", self.controller.remove_selected_equipment)

    def get_search_query(self):
        return self.search_var.get()

    def insert_result(self, values, ankama_id):
            self.results_tree.insert("", "end", values=values, tags=(ankama_id,))

    def clear_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

    def populate_results(self, results):
        for item in results:
            self.results_tree.insert("", "end", values=(item['name'], item['level'], item['type']), tags=(item['ankama_id'],))

    def get_selected_results(self):
        return self.results_tree.selection()

    def get_result_values(self, item):
        return self.results_tree.item(item)['values']

    def get_result_ankama_id(self, item):
        return self.results_tree.item(item)['tags'][0]

    def insert_equipment(self, ankama_id, values):
        return self.equipment_tree.insert("", "end", values=values, tags=(ankama_id,))

    def get_equipment_children(self):
        return self.equipment_tree.get_children()

    def get_equipment_item_tags(self, item):
        return self.equipment_tree.item(item)['tags']

    def set_equipment_value(self, item, column, value):
        self.equipment_tree.set(item, column, value)

    def get_equipment_value(self, item, column):
        return self.equipment_tree.set(item, column)

    def clear_ingredients(self):
        for item in self.ingredients_tree.get_children():
            self.ingredients_tree.delete(item)

    def insert_ingredient(self, values):
        self.ingredients_tree.insert("", "end", values=values)

    def clear_intermediate_items(self):
        for item in self.intermediate_tree.get_children():
            self.intermediate_tree.delete(item)

    def insert_intermediate_item(self, values):
        self.intermediate_tree.insert("", "end", values=values)

    def set_equipment_tags(self, item, tags):
        self.equipment_tree.item(item, tags=tags)

    def create_edit_entry(self, parent, item, column):
        x, y, width, height = parent.bbox(item, column)
        value = parent.set(item, column)
        entry = ttk.Entry(parent, width=width//8)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.select_range(0, tk.END)
        entry.focus()
        return entry