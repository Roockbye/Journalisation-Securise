from datetime import datetime, timedelta
import random

#Utilisateurs simulés
USERS = [
    "admin", "analyst", "john doe", "alice",
    "service_account", "root", "administrateur", "guest", "user1", "user2"
]

#Actions typiques
ACTIONS = [
    "login attempt", "file access", "config change", "password change",
    "data export", "logout", "system update", "file upload", "file delete", "network scan"
]

#Statuts possibles
STATUSES = ["success", "failed"]

#Adresses IP internes (10.0.0.1 à 10.0.4.254)
IPS = [f"10.0.{i}.{j}" for i in range(0, 5) for j in range(1, 255)]

#Associe un utilisateur à une IP fixe
USER_IP_MAP = {}

def get_user_ip(user):
    """Assigne une IP unique à chaque utilisateur."""
    if user not in USER_IP_MAP:
        ip = random.choice(IPS)
        USER_IP_MAP[user] = ip
        IPS.remove(ip)
    return USER_IP_MAP[user]

#Génère un log simulé cohérent
def generate_log():
    timestamp = datetime.utcnow() - timedelta(seconds=random.randint(0, 3600))
    user = random.choice(USERS)
    ip = get_user_ip(user)
    action = random.choice(ACTIONS)
    status = random.choices(STATUSES, weights=[0.8, 0.2])[0]  #80 % success, 20 % failed

    return {
        "timestamp": timestamp.isoformat() + "Z",
        "ip": ip,
        "user": user,
        "action": action,
        "status": status
    }
