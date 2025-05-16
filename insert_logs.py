from pymongo import MongoClient
from datetime import datetime, timedelta
import hashlib
import random
from logs_generator import generate_log


# Connexion MongoDB locale
client = MongoClient("mongodb://localhost:27017/")
db = client["secure_logs"]
collection = db["logs"]

# Données simulées
USERS = ["admin", "analyst", "john doe", "alice", "service account", "root", "administrateur", "guest", "user1", "user2"]
ACTIONS = ["login attempt", "file access", "config change", "password change", "data export", "logout", "system update", "file upload", "file delete", "network scan"]
STATUSES = ["success", "failed"]
IPS = [f"10.0.{i}.{j}" for i in range(0, 5) for j in range(1, 255)]  # 10.0.0.1 à 10.0.4.254

#Génération d’un log simulé
def generate_log():
    timestamp = datetime.utcnow() - timedelta(seconds=random.randint(0, 3600))
    ip = random.choice(IPS)
    user = random.choice(USERS)
    action = random.choice(ACTIONS)
    status = random.choices(STATUSES, weights=[0.8, 0.2])[0]  # 80% success, 20% failed

    return {
        "timestamp": timestamp.isoformat() + "Z",
        "ip": ip,
        "user": user,
        "action": action,
        "status": status
    }

# Calcul d’un hash d’intégrité SHA-256
def compute_log_hash(log):
    data = f"{log['timestamp']}{log['ip']}{log['user']}{log['action']}{log['status']}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# Insertion d’un lot de logs
def insert_logs(n=100):
    inserted = 0
    for _ in range(n):
        log = generate_log()
        log["log_hash"] = compute_log_hash(log)
        result = collection.insert_one(log)
        inserted += 1
    print(f"{inserted} logs insérés dans la base 'secure_logs.logs'.")

# Lancement
if __name__ == "__main__":
    insert_logs(n=100)
