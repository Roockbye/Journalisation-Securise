from pymongo import MongoClient
from datetime import datetime
import re

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
collection = client["secure_logs"]["logs"]

def detect_failed_login_bursts():
    print(" IPs avec >5 échecs en 10 minutes :")
    pipeline = [
        {"$match": { "status": "failed" }},
        {"$project": {
            "ip": 1,
            "timestamp": {
                "$dateFromString": { "dateString": "$timestamp" }
            }
        }},
        {"$group": {
            "_id": {
                "ip": "$ip",
                "minute": { "$dateTrunc": {
                    "date": "$timestamp",
                    "unit": "minute",
                    "binSize": 10
                }}
            },
            "count": { "$sum": 1 }
        }},
        {"$match": { "count": { "$gt": 5 } }},
        {"$sort": { "count": -1 }}
    ]

    results = collection.aggregate(pipeline)
    for res in results:
        ip = res["_id"]["ip"]
        ts = res["_id"]["minute"].isoformat()
        count = res["count"]
        print(f" - {ip} → {count} échecs entre {ts} et +10min")

def detect_unknown_ip_ranges():
    print("\n Connexions depuis des IP hors plage 10.0.x.x :")
    pattern = re.compile(r"^10\.0\.\d{1,3}\.\d{1,3}$")

    ips = collection.distinct("ip")
    for ip in ips:
        if not pattern.match(ip):
            print(f" - IP inconnue : {ip}")

def detect_suspicious_hours():
    print("\n Accès à des heures inhabituelles (0h–5h UTC) :")
    logs = collection.find({}, {"ip": 1, "timestamp": 1})
    for log in logs:
        try:
            dt = datetime.fromisoformat(log["timestamp"].replace("Z", ""))
            if 0 <= dt.hour < 5:
                print(f" - {log['ip']} à {dt.isoformat()}")
        except Exception as e:
            print(f"Erreur horodatage : {log.get('timestamp')} → {e}")

if __name__ == "__main__":
    detect_failed_login_bursts()
    detect_unknown_ip_ranges()
    detect_suspicious_hours()
