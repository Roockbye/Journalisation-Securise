from flask import Flask, request, render_template_string, jsonify
from db_connector import get_db
from datetime import datetime
import re

app = Flask(__name__)
db = get_db()
collection = db["logs"]

TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Journalisation Sécurisée</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container my-5">
    <h1 class="mb-4">Journalisation Sécurisée</h1>

    <form class="row g-3 mb-4" method="get" action="/logs">
        <div class="col-md-2">
            <input type="text" class="form-control" name="ip" placeholder="IP">
        </div>
        <div class="col-md-2">
            <input type="text" class="form-control" name="user" placeholder="Utilisateur">
        </div>
        <div class="col-md-2">
            <input type="text" class="form-control" name="action" placeholder="Action">
        </div>
        <div class="col-md-2">
            <input type="text" class="form-control" name="status" placeholder="Statut">
        </div>
        <div class="col-md-2">
            <input type="date" class="form-control" name="date" placeholder="Date">
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-primary w-100">Rechercher</button>
        </div>
    </form>

    {% if logs %}
    <div class="table-responsive">
        <table class="table table-striped table-bordered align-middle">
            <thead class="table-dark">
                <tr>
                    <th>Horodatage</th>
                    <th>IP</th>
                    <th>Utilisateur</th>
                    <th>Action</th>
                    <th>Statut</th>
                    <th>Hash d'intégrité</th>
                </tr>
            </thead>
            <tbody>
                {% for log in logs %}
                <tr>
                    <td>{{ log.timestamp }}</td>
                    <td>{{ log.ip }}</td>
                    <td>{{ log.user }}</td>
                    <td>{{ log.action }}</td>
                    <td>
                        {% if log.status == "success" %}
                        <span class="badge bg-success">{{ log.status }}</span>
                        {% else %}
                        <span class="badge bg-danger">{{ log.status }}</span>
                        {% endif %}
                    </td>
                    <td style="font-size: 10px;">{{ log.log_hash }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% elif logs is not none %}
    <div class="alert alert-warning">Aucun log trouvé pour cette recherche.</div>
    {% endif %}

    {% if anomalies %}
    <hr class="my-5">
    <h2>Anomalies détectées</h2>

    {% if anomalies.failed_login_bursts %}
    <h5 class="mt-4">Tentatives de connexions échouées (≥ 5 en 10 min)</h5>
    <ul class="list-group mb-3">
        {% for a in anomalies.failed_login_bursts %}
        <li class="list-group-item">
            IP <strong>{{ a.ip }}</strong> → {{ a.count }} échecs entre {{ a.window_start }}
        </li>
        {% endfor %}
    </ul>
    {% endif %}

    {% if anomalies.unknown_ip_ranges %}
    <h5>IPs hors plage 10.0.x.x</h5>
    <ul class="list-group mb-3">
        {% for ip in anomalies.unknown_ip_ranges %}
        <li class="list-group-item text-danger">{{ ip }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    {% if anomalies.suspicious_hours %}
    <h5>Accès entre 00h et 05h UTC</h5>
    <ul class="list-group mb-3">
        {% for a in anomalies.suspicious_hours %}
        <li class="list-group-item">
            {{ a.ip }} à {{ a.timestamp }}
        </li>
        {% endfor %}
    </ul>
    {% endif %}
    {% endif %}
</div>
</body>
</html>
"""

def get_anomalies():
    anomalies = {
        "failed_login_bursts": [],
        "unknown_ip_ranges": [],
        "suspicious_hours": []
    }

    # 1. >5 échecs en 10 minutes
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
    for res in collection.aggregate(pipeline):
        anomalies["failed_login_bursts"].append({
            "ip": res["_id"]["ip"],
            "window_start": res["_id"]["minute"].isoformat(),
            "count": res["count"]
        })

    # 2. IPs inconnues
    known_ip_pattern = re.compile(r"^10\.0\.\d{1,3}\.\d{1,3}$")
    for ip in collection.distinct("ip"):
        if not known_ip_pattern.match(ip):
            anomalies["unknown_ip_ranges"].append(ip)

    # 3. Heures suspectes
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

@app.route("/")
@app.route("/logs", methods=["GET"])
def show_logs():
    query = {}
    ip = request.args.get("ip")
    user = request.args.get("user")
    action = request.args.get("action")
    status = request.args.get("status")
    date = request.args.get("date")

    if ip: query["ip"] = ip
    if user: query["user"] = user
    if action: query["action"] = action
    if status: query["status"] = status
    if date: query["timestamp"] = {"$regex": f"^{date}"}

    logs = list(collection.find(query if query else {}, {"_id": 0}))
    anomalies = get_anomalies()
    return render_template_string(TEMPLATE, logs=logs, anomalies=anomalies)

@app.route("/api/anomalies", methods=["GET"])
def api_anomalies():
    anomalies = get_anomalies()
    return jsonify(anomalies)

if __name__ == "__main__":
    app.run(debug=True)
