from pymongo import MongoClient
client = MongoClient()


def insert_many_items(db_name, collection_name, items_to_save):
    try:
        db = client[db_name]
        cll = db[collection_name]  # cll for collection
        print("Inserting regions to db....")
        result = cll.insert_many(items_to_save)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")


def select_all(db_name, collection_name):
    try:
        db = client[db_name]
        cll = db[collection_name]
        items = list(cll.find())
        return items
    except Exception as e:
        print(f"An error occurred: {e}")
