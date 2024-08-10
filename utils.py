# utils.py

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