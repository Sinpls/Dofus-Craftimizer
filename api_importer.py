import requests
import json
import os
import time

def check_files_exist():
    data_files = [
        'dofus_resources.json',
        'dofus_consumables.json',
        'dofus_equipment.json'
    ]
    return all(os.path.exists(filename) for filename in data_files)

def check_file_age(filename):
    if not os.path.exists(filename):
        return True
    current_time = time.time()
    file_age = current_time - os.path.getmtime(filename)
    return file_age > 24 * 3600  # 24 hours in seconds

def update_json_file(url, filename):
    if check_file_age(filename):
        headers = {'Accept-Encoding': 'gzip'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
        print(f"Updated {filename}")
    else:
        print(f"{filename} is up to date")

def update_dofus_data(status_callback=None):
    data_files = {
        'dofus_resources.json': 'https://api.dofusdu.de/dofus2/en/items/resources/all?sort%5Blevel%5D=desc',
        'dofus_consumables.json': 'https://api.dofusdu.de/dofus2/en/items/consumables/all?sort%5Blevel%5D=desc',
        'dofus_equipment.json': 'https://api.dofusdu.de/dofus2/en/items/equipment/all?sort%5Blevel%5D=desc'
    }

    for filename, url in data_files.items():
        if status_callback:
            status_callback(f"Updating {filename}...")
        update_json_file(url, filename)

    if status_callback:
        status_callback("Data update complete")