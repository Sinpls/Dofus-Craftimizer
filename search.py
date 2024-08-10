import json
import os
import re

def search_json(file_name, search_term, exact_ankama_id=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    results = []
    for item in data['items']:
        if exact_ankama_id is not None:
            if item['ankama_id'] == exact_ankama_id:
                results.append({
                    'ankama_id': item['ankama_id'],
                    'name': item['name'],
                    'level': item.get('level', 'N/A'),
                    'type': item.get('type', 'N/A'),
                    'recipe': item.get('recipe', [])
                })
                break  # We found the exact match, no need to continue searching
        elif search_term.lower() in item['name'].lower():
            results.append({
                'ankama_id': item['ankama_id'],
                'name': item['name'],
                'level': item.get('level', 'N/A'),
                'type': item.get('type', 'N/A'),
                'recipe': item.get('recipe', [])
            })
    
    return results

def find_item_by_id(ankama_id):
    # Search in resources
    result = search_json('dofus_resources.json', '', exact_ankama_id=ankama_id)
    if result:
        return result[0]
    
    # If not found in resources, search in equipment
    result = search_json('dofus_equipment.json', '', exact_ankama_id=ankama_id)
    if result:
        return result[0]
    
    # If not found in equipment, search in consumables
    result = search_json('dofus_consumables.json', '', exact_ankama_id=ankama_id)
    if result:
        return result[0]
    
    return None

def find_resource_by_id(ankama_id):
    item = find_item_by_id(ankama_id)
    return item['name'] if item else None

def get_item_details(ankama_id):
    return find_item_by_id(ankama_id)

def test_find_resource():
    test_id = 2652
    result = find_resource_by_id(test_id)
    if result:
        print(f"Resource with ID {test_id} is: {result}")
    else:
        print(f"No resource found with ID {test_id}")

# Run the test function
if __name__ == "__main__":
    test_find_resource()