import tkinter as tk
from tkinter import ttk

class StyledDofusCraftimizerUI:
    def __init__(self, master, controller):
        self.master = master
        self.controller = controller
        self.master.title("Dofus Craftimizer")

        self.create_styles()
        self.create_widgets()

        self.master.update()
        self.master.geometry('')  # This resets the window size to fit its contents
        self.master.minsize(self.master.winfo_width(), self.master.winfo_height())
        self.last_clicked_tree = None

    def create_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use the 'clam' theme as a base

        # Define colors
        bg_dark = '#141414'
        bg_light = '#1F1F1F'
        light_grey = '#ADADAD'
        border_color = '#2A2A2A'  # Darker border color to blend with the background
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

        # Configure Treeview styles
        self.style.configure('Treeview', background=bg_dark, fieldbackground=bg_dark, foreground=light_grey, bordercolor=border_color, highlightthickness=0)
        self.style.configure('Treeview.Heading', background=bg_light, foreground=light_grey, font=('Arial', 10, 'bold'), bordercolor=border_color, relief='flat')
        self.style.map('Treeview', background=[('selected', accent_color)], foreground=[('selected', bg_dark)])
        self.style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

        # Configure custom styles
        self.style.configure('Search.TEntry', font=('Arial', 12), bordercolor=border_color)
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
        main_frame = ttk.Frame(self.master, style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Search frame
        search_frame = ttk.Frame(main_frame, style='Card.TFrame')
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40, style='Search.TEntry')
        search_entry.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky=(tk.W, tk.E))
        search_entry.bind("<Return>", self.controller.search_equipment)

        # Results and Equipment frame
        results_equipment_frame = ttk.Frame(main_frame, style='TFrame')
        results_equipment_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_equipment_frame.columnconfigure(0, weight=1)
        results_equipment_frame.columnconfigure(1, weight=1)
        results_equipment_frame.rowconfigure(0, weight=1)

        # Search results frame
        results_frame = ttk.LabelFrame(results_equipment_frame, text="Search Results", style='Card.TLabelframe')
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.results_tree = ttk.Treeview(results_frame, columns=("Name", "Level", "Type"), show="headings", style='Treeview', height=10)
        self.results_tree.heading("Name", text="Name")
        self.results_tree.heading("Level", text="Level")
        self.results_tree.heading("Type", text="Type")
        self.results_tree.column("Name", width=150)
        self.results_tree.column("Level", width=50)
        self.results_tree.column("Type", width=100)
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(1, 0), pady=(1, 1))

        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview, style="Custom.Vertical.TScrollbar")
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=(1, 1))
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        # Equipment list frame
        equipment_frame = ttk.LabelFrame(results_equipment_frame, text="Equipment List", style='Card.TLabelframe')
        equipment_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        equipment_frame.columnconfigure(0, weight=1)
        equipment_frame.rowconfigure(0, weight=1)

        self.equipment_tree = ttk.Treeview(equipment_frame, columns=("Name", "Amount", "Cost per Unit", "Sell Price", "Profit"), show="headings", style='Treeview', height=10)
        self.equipment_tree.heading("Name", text="Name")
        self.equipment_tree.heading("Amount", text="Amount")
        self.equipment_tree.heading("Cost per Unit", text="Cost per Unit")
        self.equipment_tree.heading("Sell Price", text="Sell Price")
        self.equipment_tree.heading("Profit", text="Profit")
        self.equipment_tree.column("Name", width=150)
        self.equipment_tree.column("Amount", width=50)
        self.equipment_tree.column("Cost per Unit", width=80)
        self.equipment_tree.column("Sell Price", width=80)
        self.equipment_tree.column("Profit", width=80)
        self.equipment_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(1, 0), pady=(1, 1))

        equipment_scrollbar = ttk.Scrollbar(equipment_frame, orient="vertical", command=self.equipment_tree.yview, style="Custom.Vertical.TScrollbar")
        equipment_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=(1, 1))
        self.equipment_tree.configure(yscrollcommand=equipment_scrollbar.set)

        # Ingredients and Intermediate Items frame
        ingredients_intermediate_frame = ttk.Frame(main_frame, style='TFrame')
        ingredients_intermediate_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        ingredients_intermediate_frame.columnconfigure(0, weight=1)
        ingredients_intermediate_frame.columnconfigure(1, weight=1)
        ingredients_intermediate_frame.rowconfigure(0, weight=1)

        # Intermediate items frame
        intermediate_frame = ttk.LabelFrame(ingredients_intermediate_frame, text="Intermediate Items", style='Card.TLabelframe')
        intermediate_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        intermediate_frame.columnconfigure(0, weight=1)
        intermediate_frame.rowconfigure(0, weight=1)

        self.intermediate_tree = ttk.Treeview(intermediate_frame, columns=("Name", "Amount", "Cost", "Level"), show="headings", style='Treeview', height=10)
        self.intermediate_tree.heading("Name", text="Name")
        self.intermediate_tree.heading("Amount", text="Amount")
        self.intermediate_tree.heading("Cost", text="Cost")
        self.intermediate_tree.heading("Level", text="Level")
        self.intermediate_tree.column("Name", width=150)
        self.intermediate_tree.column("Amount", width=50)
        self.intermediate_tree.column("Cost", width=80)
        self.intermediate_tree.column("Level", width=50)
        self.intermediate_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(1, 0), pady=(1, 1))

        intermediate_scrollbar = ttk.Scrollbar(intermediate_frame, orient="vertical", command=self.intermediate_tree.yview, style="Custom.Vertical.TScrollbar")
        intermediate_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=(1, 1))
        self.intermediate_tree.configure(yscrollcommand=intermediate_scrollbar.set)

        # Ingredients list frame
        ingredients_frame = ttk.LabelFrame(ingredients_intermediate_frame, text="Ingredients List", style='Card.TLabelframe')
        ingredients_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        ingredients_frame.columnconfigure(0, weight=1)
        ingredients_frame.rowconfigure(0, weight=1)

        self.ingredients_tree = ttk.Treeview(ingredients_frame, columns=("Name", "Amount", "Cost", "Type"), show="headings", style='Treeview', height=12)
        self.ingredients_tree.heading("Name", text="Name")
        self.ingredients_tree.heading("Amount", text="Amount")
        self.ingredients_tree.heading("Cost", text="Cost")
        self.ingredients_tree.heading("Type", text="Type")
        self.ingredients_tree.column("Name", width=150)
        self.ingredients_tree.column("Amount", width=50)
        self.ingredients_tree.column("Cost", width=80)
        self.ingredients_tree.column("Type", width=100)
        self.ingredients_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(1, 0), pady=(1, 1))

        ingredients_scrollbar = ttk.Scrollbar(ingredients_frame, orient="vertical", command=self.ingredients_tree.yview, style="Custom.Vertical.TScrollbar")
        ingredients_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=(1, 1))
        self.ingredients_tree.configure(yscrollcommand=ingredients_scrollbar.set)

        # Define tags for color coding
        self.equipment_tree.tag_configure('profit', background='#2E4A1F')  # Darker green
        self.equipment_tree.tag_configure('loss', background='#4A1F1F')  # Darker red

        # Bind events
        self.equipment_tree.bind("<Double-1>", self.on_equipment_double_click)
        self.ingredients_tree.bind("<Double-1>", self.on_ingredient_double_click)
        self.intermediate_tree.bind("<Double-1>", self.on_intermediate_double_click)
        self.results_tree.bind("<Double-1>", self.controller.add_to_equipment_list)
        self.equipment_tree.bind("<Delete>", self.controller.remove_selected_equipment)

        # Bind deselect_all_trees to main_frame
        main_frame.bind("<Button-1>", self.deselect_all_trees)

        # Update tree bindings to handle selections
        self.equipment_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.equipment_tree))
        self.ingredients_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.ingredients_tree))
        self.intermediate_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.intermediate_tree))
        self.results_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.results_tree))

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