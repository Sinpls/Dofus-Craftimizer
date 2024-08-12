import json
import os
import sys
from functools import lru_cache

class DataAccess:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            # We are running in a bundle (packaged executable)
            self.current_dir = sys._MEIPASS
        else:
            # We are running in a normal Python environment
            self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.data_dir = os.path.join(self.current_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)

    @lru_cache(maxsize=3)
    def _load_json_file(self, file_name):
        file_path = os.path.join(self.data_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return {"items": []}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_path}")
            return {"items": []}

    def search_items(self, file_name, search_term, exact_ankama_id=None):
        data = self._load_json_file(file_name)
        results = []
        for item in data['items']:
            if exact_ankama_id is not None:
                if item['ankama_id'] == exact_ankama_id:
                    results.append(self._extract_item_data(item))
                    break
            elif search_term.lower() in item['name'].lower():
                results.append(self._extract_item_data(item))
        return results

    def _extract_item_data(self, item):
        return {
            'ankama_id': item['ankama_id'],
            'name': item['name'],
            'level': item.get('level', 'N/A'),
            'type': item.get('type', 'N/A'),
            'recipe': item.get('recipe', [])
        }

    def find_item_by_id(self, ankama_id):
        for file_name in ['dofus_resources.json', 'dofus_equipment.json', 'dofus_consumables.json']:
            result = self.search_items(file_name, '', exact_ankama_id=ankama_id)
            if result:
                return result[0]
        return None

    def find_resource_by_id(self, ankama_id):
        item = self.find_item_by_id(ankama_id)
        return item['name'] if item else None

    def search_json(self, file_name, search_term, exact_ankama_id=None):
        return self.search_items(file_name, search_term, exact_ankama_id)

    def get_item_details(self, ankama_id):
        return self.find_item_by_id(ankama_id)

data_access = DataAccess()  # Create a single instance to be used across the application