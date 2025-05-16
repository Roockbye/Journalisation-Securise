from flask import Flask, request, render_template, jsonify, Response
from db_connector import get_db
from datetime import datetime
import re
import csv
import io

app = Flask(__name__)
db = get_db()
collection = db["logs"]


#Détection d'anomalies dans les logs
def get_anomalies():
    anomalies = {
        "failed_login_bursts": [],
        "unknown_ip_ranges": [],
        "suspicious_hours": []
    }

    #Requêtes d'agrégation pour les échecs groupés par tranche de 10 min
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

    for res in collection.aggregate(pipeline):
        anomalies["failed_login_bursts"].append({
            "ip": res["_id"]["ip"],
            "window_start": res["_id"]["minute"].isoformat(),
            "count": res["count"]
        })

    #IPs hors de la plage 10.0.x.x
    known_ip_pattern = re.compile(r"^10\.0\.\d{1,3}\.\d{1,3}$")
    for ip in collection.distinct("ip"):
        if not known_ip_pattern.match(ip):
            anomalies["unknown_ip_ranges"].append(ip)

    #Accès entre 00h et 05h UTC
    logs = collection.find({}, {"ip": 1, "timestamp": 1})
    for log in logs:
        try:
            dt = datetime.fromisoformat(log["timestamp"].replace("Z", ""))
            if 0 <= dt.hour < 5:
                anomalies["suspicious_hours"].append({
                    "ip": log["ip"],
                    "timestamp": log["timestamp"]
                })
        except Exception:
            continue

    return anomalies


#Page d'accueil avec liens vers les fonctions principales
@app.route("/")
def home():
    return render_template("home.html")


#Affichage des logs avec filtres et anomalies
@app.route("/logs", methods=["GET"])
def show_logs():
    query = {}
    ip = request.args.get("ip")
    user = request.args.get("user")
    action = request.args.get("action")
    status = request.args.get("status")
    date = request.args.get("date")

    #Construction de la requête de recherche
    if ip: query["ip"] = ip
    if user: query["user"] = user
    if action: query["action"] = action
    if status: query["status"] = status
    if date: query["timestamp"] = {"$regex": f"^{date}"}

    #Récupération des logs + détection d'anomalies
    logs = list(collection.find(query if query else {}, {"_id": 0}))
    anomalies = get_anomalies()
    return render_template("api.html", logs=logs, anomalies=anomalies)


#Export des logs en fichier CSV téléchargeable
@app.route("/export")
def export_logs():
    logs = collection.find({}, {"_id": 0})
    output = io.StringIO()

    # Inclure log_id dans les colonnes
    writer = csv.DictWriter(output, fieldnames=["log_id", "timestamp", "ip", "user", "action", "status", "log_hash"])
    writer.writeheader()

    for log in logs:
        writer.writerow(log)

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=logs.csv"
    return response


#Affichage d’un dashboard interactif avec graphiques
@app.route("/dashboard")
def dashboard():
    #Regroupement par statut (success/failed)
    pipeline_status = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    #Regroupement par heure d'activité
    pipeline_hour = [
        {"$project": {
            "hour": {"$substr": ["$timestamp", 11, 2]}
        }},
        {"$group": {"_id": "$hour", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    #Top IPs avec échecs de connexion
    pipeline_ip = [
        {"$match": {"status": "failed"}},
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]

    stats_status = list(collection.aggregate(pipeline_status))
    stats_hour = list(collection.aggregate(pipeline_hour))
    stats_ip = list(collection.aggregate(pipeline_ip))

    return render_template("dashboard.html", stats_status=stats_status, stats_hour=stats_hour, stats_ip=stats_ip)


#API JSON pour récupérer les anomalies
@app.route("/api/anomalies", methods=["GET"])
def api_anomalies():
    anomalies = get_anomalies()
    return jsonify(anomalies)


#Lancement de l'application
if __name__ == "__main__":
    app.run(debug=True)