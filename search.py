import json
import os
import re

def search_json(file_name, search_term):
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full file path
    file_path = os.path.join(current_dir, file_name)
    
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Compile a case-insensitive regular expression for the search term
    search_regex = re.compile(search_term, re.IGNORECASE)
    
    # Find all matches in the "name" field only
    results = []
    for item in data['items']:
        if search_regex.search(item['name']):
            results.append({
                'ankama_id': item['ankama_id'],
                'name': item['name'],
                'level': item.get('level', 'N/A'),
                'type': item.get('type', 'N/A'),
                'recipe': item.get('recipe', [])  # Make sure to include the recipe
            })
    
    return results

def find_resource_by_id(ankama_id):
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full file path for dofus_resources.json
    file_path = os.path.join(current_dir, 'dofus_resources.json')
    
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Search for the item with the given ankama_id
    for item in data['items']:
        if item['ankama_id'] == ankama_id:
            return item['name']
    
    # If no item is found, return None
    return None

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