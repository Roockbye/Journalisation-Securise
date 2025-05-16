import csv
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["secure_logs"]
collection = db["logs"]

with open("secure_logs.logs.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    data = [row for row in reader]

collection.insert_many(data)
print(f"{len(data)} logs insérés depuis CSV.")
