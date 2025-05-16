from pymongo import MongoClient
from datetime import datetime, timedelta
import hashlib
import hmac
import random
import uuid
from db_connector import get_db
from logs_generator import generate_log

#Connexion à MongoDB locale (port par défaut 27017)
db = get_db()
collection = db["logs"]

#Clé secrète pour le HMAC
SECRET_KEY = b"supersecretkey123"

#Utilisateurs fictifs
USERS = [
    "admin", "analyst", "john doe", "alice",
    "service account", "root", "administrateur", "guest", "user1", "user2"
]

#Actions simulées
ACTIONS = [
    "login attempt", "file access", "config change", "password change",
    "data export", "logout", "system update", "file upload", "file delete", "network scan"
]

#Statuts possibles
STATUSES = ["success", "failed"]

#Génération d’adresses IP internes (10.0.0.1 à 10.0.4.254)
IPS = [f"10.0.{i}.{j}" for i in range(0, 5) for j in range(1, 255)]


#Génère un log simulé
def generate_log():
    timestamp = datetime.utcnow() - timedelta(seconds=random.randint(0, 3600))
    ip = random.choice(IPS)
    user = random.choice(USERS)
    action = random.choice(ACTIONS)
    status = random.choices(STATUSES, weights=[0.8, 0.2])[0]  # 80 % de succès

    return {
        "log_id": uuid.uuid4().hex,
        "timestamp": timestamp.isoformat() + "Z",
        "ip": ip,
        "user": user,
        "action": action,
        "status": status
    }


#Calcule un HMAC-SHA256 pour garantir l’intégrité du log
def compute_log_hash(log):
    message = f"{log['log_id']}{log['timestamp']}{log['ip']}{log['user']}{log['action']}{log['status']}"
    return hmac.new(SECRET_KEY, message.encode('utf-8'), hashlib.sha256).hexdigest()


#Insère un lot de logs simulés dans MongoDB
def insert_logs(n=100):
    inserted = 0
    for _ in range(n):
        log = generate_log()
        log["log_hash"] = compute_log_hash(log)  # Ajout du hash
        collection.insert_one(log)
        inserted += 1

    print(f"{inserted} logs insérés dans la base 'secure_logs.logs'")


#Lancement
if __name__ == "__main__":
    insert_logs(n=100)
