from pymongo import MongoClient
from pymongo.errors import ConfigurationError

from pprint import pprint

try:
    client = MongoClient(
        'mongodb+srv://kp_root:KPUser22@kp-work.4fzwv.mongodb.net/kplc_region_demo?retryWrites=true&w=majority'
    )
except ConfigurationError as ce:
    print(f'ERROR: {ce}')


def insert_many_items(db_name, collection_name, items_to_save):
    try:
        db = client[db_name]
        cll = db[collection_name]  # cll for collection
        print("Inserting regions to db....")
        result = cll.insert_many(items_to_save)
        print("Successfully inserted items to db")
    except Exception as e:
        print(f"An error occurred: {e}")


def select_all(db_name, collection_name):
    try:
        db = client[db_name]
        cll = db[collection_name]
        items = list(cll.find())
        pprint(items)
        return items
    except Exception as e:
        print(f"An error occurred: {e}")
