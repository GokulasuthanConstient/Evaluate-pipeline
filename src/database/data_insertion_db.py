import json
from pymongo import MongoClient
from src.configs.path import EXTRACTED_PATH

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  #MonogDB connection string
db = client["Learning"]  #Database name
collection = db["A4_finance"]  #Collection name

# Read and insert data from the JSONL file
with open(EXTRACTED_PATH, "r", encoding="utf-8") as file:
    documents = []
    for line in file:
        line = line.strip()
        if line:  
            try:
                doc = json.loads(line)
                documents.append(doc)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    if documents:
        collection.insert_many(documents)
        print(f"Inserted {len(documents)} documents into MongoDB.")
    else:
        print("No valid documents found to insert.")
