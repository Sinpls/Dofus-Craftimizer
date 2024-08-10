# ingredient_manager.py

class Ingredient:
    def __init__(self, name, amount=0, cost=0, ingredient_type="resource"):
        self.name = name
        self.amount = amount
        self.cost = cost
        self.type = ingredient_type

class IngredientManager:
    def __init__(self):
        self.ingredients = {}

    def add_or_update_ingredient(self, name, amount, cost=None, ingredient_type="resource"):
        if name in self.ingredients:
            self.ingredients[name].amount = amount
            if cost is not None:
                self.ingredients[name].cost = cost
        else:
            self.ingredients[name] = Ingredient(name, amount, cost if cost is not None else 0, ingredient_type)

    def get_ingredients_list(self):
        return list(self.ingredients.values())

    def update_ingredient_cost(self, name, cost):
        if name in self.ingredients:
            self.ingredients[name].cost = cost

    def get_ingredient_cost(self, name):
        if name in self.ingredients:
            return self.ingredients[name].cost
        return 0

    def clear_amounts(self):
        for ingredient in self.ingredients.values():
            ingredient.amount = 0

def process_recipe(recipe, amount=1):
    ingredients = []
    for item in recipe:
        ankama_id = item['item_ankama_id']
        quantity = item['quantity']
        item_subtype = item['item_subtype']
        
        if ankama_id is not None:
            ingredients.append({
                "ankama_id": ankama_id,
                "amount": quantity * amount,
                "type": item_subtype
            })
    return ingredients