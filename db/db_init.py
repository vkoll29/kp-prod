from pymongo import MongoClient
from helpers.data_schema import generate_data_schema
from db.db_helpers import insert_many_items

client = MongoClient()
db = client.kplc_region_demo

all_locations = generate_data_schema()

insert_many_items('kplc_region_demo', 'affected_regions', all_locations)