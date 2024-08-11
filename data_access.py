import json
import os
from functools import lru_cache

class DataAccess:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

    @lru_cache(maxsize=3)  # Cache the last 3 file reads
    def _load_json_file(self, file_name):
        file_path = os.path.join(self.current_dir, file_name)
        with open(file_path, 'r') as file:
            return json.load(file)

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