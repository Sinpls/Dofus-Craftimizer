from data_access import data_access

def search_json(file_name, search_term, exact_ankama_id=None):
    return data_access.search_items(file_name, search_term, exact_ankama_id)

def find_item_by_id(ankama_id):
    return data_access.find_item_by_id(ankama_id)

def find_resource_by_id(ankama_id):
    return data_access.find_resource_by_id(ankama_id)

def get_item_details(ankama_id):
    return find_item_by_id(ankama_id)