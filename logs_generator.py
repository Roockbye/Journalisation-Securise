from datetime import datetime, timedelta
import hashlib
import random

# Données simulées
USERS = ["admin", "analyst", "john doe", "alice", "service_account", "root", "administrateur", "guest", "user1", "user2"]
ACTIONS = ["login attempt", "file access", "config change", "password change", "data export", "logout", "system update", "file upload", "file delete", "network scan"]
STATUSES = ["success", "failed"]
IPS = [f"10.0.{i}.{j}" for i in range(0, 5) for j in range(1, 255)]

USER_IP_MAP = {}

def get_user_ip(user):
    if user not in USER_IP_MAP:
        ip = random.choice(IPS)
        USER_IP_MAP[user] = ip
        IPS.remove(ip)
    return USER_IP_MAP[user]

def compute_hash(log):
    data = f"{log['timestamp']}{log['ip']}{log['user']}{log['action']}{log['status']}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def generate_log():
    timestamp = datetime.utcnow() - timedelta(seconds=random.randint(0, 3600))
    user = random.choice(USERS)
    ip = get_user_ip(user)
    action = random.choice(ACTIONS)
    status = random.choices(STATUSES, weights=[0.8, 0.2])[0]

    log = {
        "timestamp": timestamp.isoformat() + "Z",
        "ip": ip,
        "user": user,
        "action": action,
        "status": status
    }
    log["log_hash"] = compute_hash(log)
    return log
