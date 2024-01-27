import codecs
import csv
from datetime import datetime, timedelta
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd
import pymongo

from motor.motor_asyncio import AsyncIOMotorClient

async def get_mongo_client():
    load_dotenv()
    
    mongo_uri = os.getenv("MONGO_URI")
    
    client = AsyncIOMotorClient(mongo_uri, maxPoolSize=50)

    return client




async def find_data(db_name,document_name):
    mongo_client = await get_mongo_client()
    
    today = datetime.today()
    time_threshold = today - timedelta(minutes=3)


    data = await mongo_client[db_name][f'{document_name}'].find_one({
        "$or": [
            {
                "$and": [
                    {"updated_at": {"$lt": time_threshold}},
                    {"updated_at": {"$exists": True}},
                    {"generated": "Error"},
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
    print(data)
    # Check if data is found
    if data:
        # Assuming you have an "_id" field in your document
        object_id = data["_id"]
        mongo_client[db_name][f'{document_name}'].update_one(
            {"_id": object_id},
            {"$set": {"updated_at": datetime.now()}}
        )
        del data['_id']
        return data
    else:
        return "No Data Found"
        
            
async def insert_to_mongodb(df, database_name, document_name):
    try: 
        client = await get_mongo_client()
        
        # Access the specified database
        db = client[database_name]
        
        # Access the specified collection
        collection = db[document_name]

        # Create a unique index on the "Dissemination Identifier" field
        collection.create_index([("id", pymongo.DESCENDING)], unique=True)
        
        # Insert the list of dictionaries into the collection
        records = df.to_dict(orient='records')
        
        collection.insert_many(records)
        
    except Exception as e: 
        print(e)



async def update_data(data, database_name, document_name):
    print('data',data.id, data.text)
    mongo_client = await get_mongo_client()
    updated_data = await mongo_client[database_name][f'{document_name}'].update_one(
        {"id": data.id},
        {"$set": {"generated": data.text}}
    )
    if updated_data.matched_count == 1: 
        return "document updated"
    else: 
        return "document update failed"
