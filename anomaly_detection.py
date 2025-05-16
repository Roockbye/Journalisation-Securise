from pymongo import MongoClient
from datetime import datetime
import re

client = MongoClient("mongodb://localhost:27017/")
collection = client["secure_logs"]["logs"]

#Détecte les IP ayant provoqué >5 échecs en 10 minutes
def detect_failed_login_bursts():
    print("\n🔐 IPs avec plus de 5 échecs de connexion en 10 minutes :")
    pipeline = [
        {"$match": {"status": "failed"}},
        {"$project": {
            "ip": 1,
            "timestamp": {"$dateFromString": {"dateString": "$timestamp"}}
        }},
        {"$group": {
            "_id": {
                "ip": "$ip",
                "minute": {"$dateTrunc": {
                    "date": "$timestamp",
                    "unit": "minute",
                    "binSize": 10
                }}
            },
            "count": {"$sum": 1}
        }},
        {"$match": {"count": {"$gt": 5}}},
        {"$sort": {"count": -1}}
    ]

    results = collection.aggregate(pipeline)
    for res in results:
        ip = res["_id"]["ip"]
        start_time = res["_id"]["minute"].isoformat()
        count = res["count"]
        print(f" - {ip} → {count} échecs entre {start_time} et +10min")


#Détecte les connexions provenant de plages IP inconnues (hors 10.0.x.x)
def detect_unknown_ip_ranges():
    print("\n🌐 IPs hors plage autorisée (10.0.x.x) :")
    allowed_pattern = re.compile(r"^10\\.0\\.\\d{1,3}\\.\\d{1,3}$")

    ips = collection.distinct("ip")
    for ip in ips:
        if not allowed_pattern.match(ip):
            print(f" - IP suspecte : {ip}")


#Détecte les accès ayant lieu entre minuit et 5h du matin UTC
def detect_suspicious_hours():
    print("\n⏰ Accès détectés à des heures inhabituelles (entre 00h et 05h UTC) :")
    logs = collection.find({}, {"ip": 1, "timestamp": 1})
    for log in logs:
        try:
            dt = datetime.fromisoformat(log["timestamp"].replace("Z", ""))
            if 0 <= dt.hour < 5:
                print(f" - {log['ip']} à {dt.isoformat()}")
        except Exception as e:
            print(f"Erreur horodatage : {log.get('timestamp')} → {e}")


#Lancement
if __name__ == "__main__":
    detect_failed_login_bursts()
    detect_unknown_ip_ranges()
    detect_suspicious_hours()