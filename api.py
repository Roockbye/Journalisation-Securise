from flask import Flask, request, render_template, jsonify
from db_connector import get_db
from datetime import datetime
import re

app = Flask(__name__)
db = get_db()
collection = db["logs"]

def get_anomalies():
    anomalies = {
        "failed_login_bursts": [],
        "unknown_ip_ranges": [],
        "suspicious_hours": []
    }

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

    known_ip_pattern = re.compile(r"^10\.0\.\d{1,3}\.\d{1,3}$")
    for ip in collection.distinct("ip"):
        if not known_ip_pattern.match(ip):
            anomalies["unknown_ip_ranges"].append(ip)

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
    return render_template("api.html", logs=logs, anomalies=anomalies)


@app.route("/api/anomalies", methods=["GET"])
def api_anomalies():
    anomalies = get_anomalies()
    return jsonify(anomalies)


if __name__ == "__main__":
    app.run(debug=True)
