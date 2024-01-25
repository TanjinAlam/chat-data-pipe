from datetime import datetime, timedelta
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import os

import pymongo

def get_mongo_client():
    load_dotenv()

    mongo_host = os.getenv("MONGO_HOST")
    mongo_port = int(os.getenv("MONGO_PORT"))
    mongo_username = os.getenv("MONGO_USERNAME")
    mongo_password = os.getenv("MONGO_PASSWORD")

    client = MongoClient(
        host=mongo_host,
        port=mongo_port,
        username=mongo_username,
        password=mongo_password
    )

    return client



def find_data(db_name,instrument_name):
    mongo_client = get_mongo_client()
    
    today = datetime.today()
    time_threshold = today - timedelta(minutes=1)


    data = mongo_client[db_name][f'{instrument_name}'].find_one({
        "$or": [
            {
                "$and": [
                    {"updated_at": {"$lt": time_threshold}},
                    {"updated_at": {"$exists": True}},
                ]
            },
            {
                "$and": [
                    {"generated": "Error"},
                    {"updated_at": {"$exists": False}},
                ]
            },
        ],
    })
    # Check if data is found
    if data:
        # Assuming you have an "_id" field in your document
        object_id = data["_id"]
        mongo_client[db_name][f'{instrument_name}'].update_one(
            {"_id": object_id},
            {"$set": {"updated_at": datetime.now()}}
        )
        del data['_id']
        return data
    else:
        return "No Data Found"
        
            
def insert_to_mongodb(df, database_name, collection_name):
    client = get_mongo_client()
    
    # Access the specified database
    db = client[database_name]
    
    # Access the specified collection
    collection = db[collection_name]

    # Insert the list of dictionaries into the collection
    records = df.to_dict(orient='records')
      
    collection.insert_many(records)
