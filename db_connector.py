import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

def get_db():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    user = os.getenv("MONGO_USER")
    pwd  = os.getenv("MONGO_PASS")

    if user and pwd:
        client = MongoClient(uri, username=user, password=pwd, authSource="admin")
    else:
        client = MongoClient(uri)

    return client["secure_logs"]

