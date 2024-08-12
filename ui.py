import tkinter as tk
from tkinter import ttk

class StyledDofusCraftimizerUI:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller

        self.create_styles()
        self.create_widgets()

        self.last_clicked_tree = None

    def create_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use the 'clam' theme as a base

        # Define colors
        bg_dark = '#141414'
        bg_light = '#1F1F1F'
        light_grey = '#ADADAD'
        border_color = '#2A2A2A'
        accent_color = '#97BE0D'
        scrollbar_bg = '#2A2A2A'
        scrollbar_fg = '#4A4A4A'

        # Configure global styles
        self.style.configure('TFrame', background=bg_dark, bordercolor=border_color, highlightthickness=0)
        self.style.configure('TLabel', background=bg_dark, foreground=light_grey, font=('Arial', 10))
        self.style.configure('TEntry', fieldbackground=bg_light, foreground=light_grey, bordercolor=border_color, insertcolor=light_grey)
        self.style.map('TEntry', fieldbackground=[('focus', bg_light)])
        self.style.configure('TButton', background=bg_light, foreground=light_grey, bordercolor=border_color)
        self.style.map('TButton', background=[('active', border_color)])

        # Configure Treeview styles with larger font
        self.style.configure('Treeview', background=bg_dark, fieldbackground=bg_dark, foreground=light_grey, bordercolor=border_color, highlightthickness=0, font=('Arial', 12))
        self.style.configure('Treeview.Heading', background=bg_light, foreground=light_grey, font=('Arial', 12, 'bold'), bordercolor=border_color, relief='flat')
        self.style.map('Treeview', background=[('selected', accent_color)], foreground=[('selected', bg_dark)])
        self.style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        # Configure custom styles
        self.style.configure('Search.TEntry', padding=(5, 10), bordercolor=border_color)
        self.style.configure('Card.TFrame', background=bg_light, bordercolor=border_color, relief='solid', borderwidth=1)
        self.style.configure('Card.TLabelframe', background=bg_light, foreground=light_grey, font=('Arial', 12, 'bold'), bordercolor=border_color, relief='solid', borderwidth=1)
        self.style.configure('Card.TLabelframe.Label', background=bg_light, foreground=light_grey, font=('Arial', 12, 'bold'), padding=(10, 5))

        # Configure custom scrollbar style
        self.style.configure("Custom.Vertical.TScrollbar", background=scrollbar_bg, troughcolor=bg_dark, 
                            bordercolor=border_color, arrowcolor=light_grey, relief='flat')
        self.style.map("Custom.Vertical.TScrollbar", background=[('active', scrollbar_fg)])
        
        # Configure horizontal scrollbar if needed
        self.style.configure("Custom.Horizontal.TScrollbar", background=scrollbar_bg, troughcolor=bg_dark, 
                            bordercolor=border_color, arrowcolor=light_grey, relief='flat')
        self.style.map("Custom.Horizontal.TScrollbar", background=[('active', scrollbar_fg)])

        # Additional styles to ensure consistent borders
        self.style.configure('TSeparator', background=border_color)
        self.style.configure('TNotebook', background=bg_dark, bordercolor=border_color, tabmargins=[0, 0, 0, 0])
        self.style.configure('TNotebook.Tab', background=bg_light, foreground=light_grey, bordercolor=border_color, padding=[5, 2])
        self.style.map('TNotebook.Tab', background=[('selected', bg_dark)], foreground=[('selected', light_grey)])
        self.style.configure('Intermediate.Treeview.Row', background='#2A2A2A')  # Lighter grey color

        # Remove focus border
        self.style.layout('TEntry', [
            ('Entry.plain.field', {'children': [(
                'Entry.background', {'children': [(
                    'Entry.padding', {'children': [(
                        'Entry.textarea', {'sticky': 'nswe'})],
                    'sticky': 'nswe'})], 'sticky': 'nswe'})],
                'border': '1', 'sticky': 'nswe'})])
        
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.master, padding="10 10 10 10", style='TFrame')
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # Search frame
        search_frame = ttk.Frame(self.main_frame, style='TFrame')
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, style='Search.TEntry', width=25, font=('Arial', 18))
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5)
        search_entry.bind("<Return>", self.controller.search_equipment)

        # Results and Equipment frame
        results_equipment_frame = ttk.Frame(self.main_frame, style='TFrame')
        results_equipment_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Search results frame
        results_frame = ttk.LabelFrame(results_equipment_frame, text="Search Results", style='Card.TLabelframe')
        results_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 5))

        self.results_tree = ttk.Treeview(results_frame, columns=("Name", "Level", "Type"), show="headings", style='Treeview')
        self.results_tree.heading("Name", text="Name")
        self.results_tree.heading("Level", text="Level")
        self.results_tree.heading("Type", text="Type")
        self.results_tree.column("Name", width=200)
        self.results_tree.column("Level", width=70, anchor=tk.CENTER)
        self.results_tree.column("Type", width=130)
        self.results_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview, style="Custom.Vertical.TScrollbar")
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        # Equipment list frame
        equipment_frame = ttk.LabelFrame(results_equipment_frame, text="Equipment List", style='Card.TLabelframe')
        equipment_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(5, 0))

        self.equipment_tree = ttk.Treeview(equipment_frame, columns=("Name", "Amount", "Cost per Unit", "Sell Price", "Profit"), show="headings", style='Treeview')
        self.equipment_tree.heading("Name", text="Name")
        self.equipment_tree.heading("Amount", text="Amount")
        self.equipment_tree.heading("Cost per Unit", text="Cost per Unit")
        self.equipment_tree.heading("Sell Price", text="Sell Price")
        self.equipment_tree.heading("Profit", text="Profit")
        self.equipment_tree.column("Name", width=200)
        self.equipment_tree.column("Amount", width=80, anchor=tk.CENTER)
        self.equipment_tree.column("Cost per Unit", width=120, anchor=tk.E)
        self.equipment_tree.column("Sell Price", width=120, anchor=tk.E)
        self.equipment_tree.column("Profit", width=120, anchor=tk.E)
        self.equipment_tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        equipment_scrollbar = ttk.Scrollbar(equipment_frame, orient="vertical", command=self.equipment_tree.yview, style="Custom.Vertical.TScrollbar")
        equipment_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.equipment_tree.configure(yscrollcommand=equipment_scrollbar.set)

        # Ingredients and Intermediate Items frame
        ingredients_intermediate_frame = ttk.Frame(self.main_frame, style='TFrame')
        ingredients_intermediate_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        ingredients_intermediate_frame.columnconfigure(0, weight=6)  # 60% for ingredients
        ingredients_intermediate_frame.columnconfigure(1, weight=4)  # 40% for intermediate
        ingredients_intermediate_frame.rowconfigure(0, weight=1)  # Allow vertical expansion

        # Ingredients list frame
        ingredients_frame = ttk.LabelFrame(ingredients_intermediate_frame, text="Ingredients List", style='Card.TLabelframe')
        ingredients_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        ingredients_frame.rowconfigure(0, weight=1)
        ingredients_frame.columnconfigure(0, weight=1)

        self.ingredients_tree = ttk.Treeview(ingredients_frame, columns=("Name", "Amount", "Cost", "Type"), show="headings", style='Treeview')
        self.ingredients_tree.heading("Name", text="Name")
        self.ingredients_tree.heading("Amount", text="Amount")
        self.ingredients_tree.heading("Cost", text="Cost")
        self.ingredients_tree.heading("Type", text="Type")
        self.ingredients_tree.column("Name", width=200)
        self.ingredients_tree.column("Amount", width=80, anchor=tk.CENTER)
        self.ingredients_tree.column("Cost", width=100, anchor=tk.E)
        self.ingredients_tree.column("Type", width=130)
        self.ingredients_tree.grid(row=0, column=0, sticky="nsew")

        ingredients_scrollbar = ttk.Scrollbar(ingredients_frame, orient="vertical", command=self.ingredients_tree.yview, style="Custom.Vertical.TScrollbar")
        ingredients_scrollbar.grid(row=0, column=1, sticky="ns")
        self.ingredients_tree.configure(yscrollcommand=ingredients_scrollbar.set)

        # Intermediate items frame
        intermediate_frame = ttk.LabelFrame(ingredients_intermediate_frame, text="Intermediate Items", style='Card.TLabelframe')
        intermediate_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        intermediate_frame.rowconfigure(0, weight=1)
        intermediate_frame.columnconfigure(0, weight=1)

        self.intermediate_tree = ttk.Treeview(intermediate_frame, columns=("Name", "Amount", "Cost", "Level"), show="headings", style='Treeview')
        self.intermediate_tree.heading("Name", text="Name")
        self.intermediate_tree.heading("Amount", text="Amount")
        self.intermediate_tree.heading("Cost", text="Cost")
        self.intermediate_tree.heading("Level", text="Level")
        self.intermediate_tree.column("Name", width=160)
        self.intermediate_tree.column("Amount", width=80, anchor=tk.CENTER)
        self.intermediate_tree.column("Cost", width=80, anchor=tk.E)
        self.intermediate_tree.column("Level", width=70, anchor=tk.CENTER)
        self.intermediate_tree.grid(row=0, column=0, sticky="nsew")

        intermediate_scrollbar = ttk.Scrollbar(intermediate_frame, orient="vertical", command=self.intermediate_tree.yview, style="Custom.Vertical.TScrollbar")
        intermediate_scrollbar.grid(row=0, column=1, sticky="ns")
        self.intermediate_tree.configure(yscrollcommand=intermediate_scrollbar.set)

        # Bind events
        self.equipment_tree.bind("<Double-1>", self.on_equipment_double_click)
        self.ingredients_tree.bind("<Double-1>", self.on_ingredient_double_click)
        self.intermediate_tree.bind("<Double-1>", self.on_intermediate_double_click)
        self.results_tree.bind("<Double-1>", self.controller.add_to_equipment_list)
        self.equipment_tree.bind("<Delete>", self.controller.remove_selected_equipment)

        # Bind deselect_all_trees to main_frame
        self.main_frame.bind("<Button-1>", self.deselect_all_trees)

        # Update tree bindings to handle selections
        self.equipment_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.equipment_tree))
        self.ingredients_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.ingredients_tree))
        self.intermediate_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.intermediate_tree))
        self.results_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.results_tree))

        self.ingredients_tree.tag_configure('intermediate', background='#2A2A2A')

    def deselect_all_trees(self, event=None):
        for tree in [self.results_tree, self.equipment_tree, self.ingredients_tree, self.intermediate_tree]:
            tree.selection_remove(tree.selection())

    def get_search_query(self):
        return self.search_var.get()

    def insert_equipment(self, ankama_id, values):
        return self.equipment_tree.insert("", "end", values=values, tags=(ankama_id,))

    def clear_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

    def insert_result(self, values, ankama_id):
        self.results_tree.insert("", "end", values=values, tags=(ankama_id,))

    def populate_results(self, results):
        for item in results:
            self.results_tree.insert("", "end", values=(item['name'], item['level'], item['type']), tags=(item['ankama_id'],))

    def get_selected_results(self):
        return self.results_tree.selection()

    def get_result_values(self, item):
        return self.results_tree.item(item)['values']

    def get_result_ankama_id(self, item):
        return self.results_tree.item(item)['tags'][0]

    def insert_equipment(self, item_name, values):
        return self.equipment_tree.insert("", "end", values=values, tags=(item_name,))

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
        item = self.ingredients_tree.insert("", "end", values=values)
        if values[3] == 'Intermediate':  # Assuming the type is the fourth value
            self.ingredients_tree.item(item, tags=('intermediate',))
        return item

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
    
    def on_equipment_double_click(self, event):
        item = self.equipment_tree.identify('item', event.x, event.y)
        column = self.equipment_tree.identify_column(event.x)
        
        if column in ("#2", "#4"):  # Amount or Sell Price column
            self.edit_tree_item(self.equipment_tree, item, column)
        self.last_clicked_tree = self.equipment_tree

    def on_ingredient_double_click(self, event):
        item = self.ingredients_tree.identify('item', event.x, event.y)
        column = self.ingredients_tree.identify_column(event.x)
        
        if column == "#3":  # Cost column
            self.edit_tree_item(self.ingredients_tree, item, column)
        self.last_clicked_tree = self.ingredients_tree

    def on_intermediate_double_click(self, event):
        item = self.intermediate_tree.identify('item', event.x, event.y)
        column = self.intermediate_tree.identify_column(event.x)
        
        if column == "#3":  # Cost column
            self.edit_tree_item(self.intermediate_tree, item, column)
        self.last_clicked_tree = self.intermediate_tree

    def edit_tree_item(self, tree, item, column):
        x, y, width, height = tree.bbox(item, column)
        
        def ok(event=None):
            new_value = entry.get()
            entry.destroy()
            if new_value.strip() == '':
                new_value = '0'
            tree.set(item, column, new_value)
            self.controller.update_item(tree, item, column, new_value)

        entry = ttk.Entry(tree, width=width//8)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, tree.set(item, column))
        entry.focus_set()
        entry.bind('<Return>', ok)
        entry.bind('<FocusOut>', ok)

    def get_tree_item_values(self, tree, item):
        return tree.item(item)['values']

    def set_tree_item_value(self, tree, item, column, value):
        tree.set(item, column, value)

    def get_tree_children(self, tree):
        return tree.get_children()
    
    def on_tree_click(self, event, tree):
        if self.last_clicked_tree and self.last_clicked_tree != tree:
            self.last_clicked_tree.selection_remove(self.last_clicked_tree.selection())
        self.last_clicked_tree = tree
        tree.focus_set()

    def deselect_all_trees(self, event=None):
        for tree in [self.results_tree, self.equipment_tree, self.ingredients_tree, self.intermediate_tree]:
            tree.selection_remove(tree.selection())
        self.last_clicked_tree = None