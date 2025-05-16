import uuid
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
import hashlib
import hmac
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
SECRET_KEY = b"supersecretkey123"

if MONGO_USER and MONGO_PASS:
    client = MongoClient(MONGO_URI, username=MONGO_USER, password=MONGO_PASS)
else:
    client = MongoClient(MONGO_URI)

collection = client["secure_logs"]["logs"]


def compute_log_hash(log):
    message = f"{log['log_id']}{log['timestamp']}{log['ip']}{log['user']}{log['action']}{log['status']}"
    return hmac.new(SECRET_KEY, message.encode('utf-8'), hashlib.sha256).hexdigest()

def generate_failed_burst(ip="10.0.0.99", user="admin", count=7):
    now = datetime.utcnow()
    for i in range(count):
        ts = (now - timedelta(minutes=1)).isoformat() + "Z"
        log = {
            "log_id": uuid.uuid4().hex,
            "timestamp": ts,
            "ip": ip,
            "user": user,
            "action": "login attempt",
            "status": "failed"
        }
        log["log_hash"] = compute_log_hash(log)
        collection.insert_one(log)
    print(f"{count} logs d'échecs insérés depuis l'IP {ip}")

def generate_unknown_ip():
    log = {
        "log_id": uuid.uuid4().hex,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": "192.168.1.250",
        "user": "root",
        "action": "login attempt",
        "status": "success"
    }
    log["log_hash"] = compute_log_hash(log)
    collection.insert_one(log)
    print("Log depuis IP inconnue inséré")


def generate_suspicious_hour():
    timestamp = (datetime.utcnow().replace(hour=4, minute=15, second=0, microsecond=0)).isoformat() + "Z"
    log = {
        "log_id": uuid.uuid4().hex,
        "timestamp": timestamp,
        "ip": "10.0.0.42",
        "user": "guest",
        "action": "login attempt",
        "status": "success"
    }
    log["log_hash"] = compute_log_hash(log)
    collection.insert_one(log)
    print("Log à 4h UTC inséré")

#Lancement
if __name__ == "__main__":
    generate_failed_burst()
    generate_unknown_ip()
    generate_suspicious_hour()
    print("\n Insertion de logs anormaux terminée.")