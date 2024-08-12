import requests
import json
import os
import time
import sys

def get_data_dir():
    if getattr(sys, 'frozen', False):
        # We are running in a bundle (packaged executable)
        return os.path.join(sys._MEIPASS, 'data')
    else:
        # We are running in a normal Python environment
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def check_files_exist():
    data_dir = get_data_dir()
    data_files = [
        'dofus_resources.json',
        'dofus_consumables.json',
        'dofus_equipment.json'
    ]
    return all(os.path.exists(os.path.join(data_dir, filename)) for filename in data_files)

def check_file_age(filename):
    data_dir = get_data_dir()
    file_path = os.path.join(data_dir, filename)
    if not os.path.exists(file_path):
        return True
    current_time = time.time()
    file_age = current_time - os.path.getmtime(file_path)
    return file_age > 24 * 3600  # 24 hours in seconds

def update_json_file(url, filename):
    data_dir = get_data_dir()
    file_path = os.path.join(data_dir, filename)
    if check_file_age(filename):
        headers = {'Accept-Encoding': 'gzip'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        os.makedirs(data_dir, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
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