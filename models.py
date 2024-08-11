# models.py

class Ingredient:
    def __init__(self, name, amount, cost, ingredient_type):
        self.name = name
        self.amount = amount
        self.cost = cost
        self.type = ingredient_type

class IngredientManager:
    def __init__(self):
        self.ingredients = {}

    def add_or_update_ingredient(self, name, amount, cost, ingredient_type):
        if name in self.ingredients:
            self.ingredients[name].amount += amount
            if cost != 0:  # Only update cost if it's non-zero
                self.ingredients[name].cost = cost
        else:
            self.ingredients[name] = Ingredient(name, amount, cost, ingredient_type)

    def get_ingredient_cost(self, name):
        return self.ingredients[name].cost if name in self.ingredients else 0

    def update_ingredient_cost(self, name, cost):
        if name in self.ingredients:
            self.ingredients[name].cost = cost

    def get_ingredients_list(self):
        return list(self.ingredients.values())

    def clear_ingredients(self):
        self.ingredients.clear()

    def get_ingredient(self, name):
        return self.ingredients.get(name)

    def update_ingredient_amount(self, name, amount):
        if name in self.ingredients:
            self.ingredients[name].amount = amount

    def remove_ingredient(self, name):
            self.ingredients.pop(name, None)