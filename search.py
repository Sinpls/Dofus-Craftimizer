from data_access import data_access

def search_json(file_name, search_term, exact_ankama_id=None):
    return data_access.search_items(file_name, search_term, exact_ankama_id)

def find_item_by_id(ankama_id):
    return data_access.find_item_by_id(ankama_id)

def find_resource_by_id(ankama_id):
    return data_access.find_resource_by_id(ankama_id)

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