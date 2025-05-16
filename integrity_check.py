import os
import hashlib
import hmac
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")

SECRET_KEY = b"supersecretkey123"

if MONGO_USER and MONGO_PASS:
    client = MongoClient(MONGO_URI, username=MONGO_USER, password=MONGO_PASS)
else:
    client = MongoClient(MONGO_URI)

collection = client["secure_logs"]["logs"]

# Recalcul du hash attendu
def compute_hash(log):
    try:
        message = f"{log['log_id']}{log['timestamp']}{log['ip']}{log['user']}{log['action']}{log['status']}"
        return hmac.new(SECRET_KEY, message.encode('utf-8'), hashlib.sha256).hexdigest()
    except KeyError as e:
        return None

def verify_logs():
    ok, ko, skipped = 0, 0, 0
    for log in collection.find():
        if all(k in log for k in ['log_id', 'timestamp', 'ip', 'user', 'action', 'status', 'log_hash']):
            expected = compute_hash(log)
            if expected == log["log_hash"]:
                ok += 1
            else:
                ko += 1
                print(f"Log corrompu : log_id={log['log_id']}")
        else:
            skipped += 1
            print(f" Log ignoré (champs manquants) : {log}")
    print(f"\nLogs intègres : {ok}")
    print(f"Logs corrompus : {ko}")
    print(f"Logs ignorés : {skipped}")

if __name__ == "__main__":
    verify_logs()
