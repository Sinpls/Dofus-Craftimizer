import requests
import json

def get_dofus_resources():
    url = 'https://api.dofusdu.de/dofus2/en/items/resources/all?sort%5Blevel%5D=desc'
    headers = {'Accept-Encoding': 'gzip'}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    
    with open('dofus_resources.json', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=2)

def get_dofus_consumables():
    url = 'https://api.dofusdu.de/dofus2/en/items/consumables/all?sort%5Blevel%5D=desc'
    headers = {'Accept-Encoding': 'gzip'}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    
    with open('dofus_consumables.json', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=2)

def get_dofus_equipment():
    url = 'https://api.dofusdu.de/dofus2/en/items/equipment/all?sort%5Blevel%5D=desc'
    headers = {'Accept-Encoding': 'gzip'}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    
    with open('dofus_equipment.json', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=2)

# Call the function
get_dofus_resources()
get_dofus_equipment()
get_dofus_consumables()