# Rapport de Projet : Système de Journalisation Sécurisée

---

## 1. Architecture choisie

Le projet est basé sur une architecture modulaire composée des éléments suivants :

- **Flask** pour le serveur web et les routes API
- **MongoDB** pour le stockage NoSQL des logs
- **Bootstrap & Chart.js** pour l’interface utilisateur et les dashboards
- **Docker & Docker Compose** pour la conteneurisation
- **HMAC-SHA256** pour garantir l’intégrité des logs

Structure du projet :

```
secure-logging-system/
├── api.py                  # API Flask principale
├── db_connector.py         # Connexion MongoDB (via .env)
├── insert_logs.py          # Générateur de logs classiques
├── test_anomaly.py         # Générateur de logs anormaux (test)
├── anomaly_detection.py    # Détection d'anomalies via console
├── templates/              # Templates HTML (Flask)
├── Dockerfile              # Image Docker de l'application
├── docker-compose.yml      # Stack Flask + MongoDB
├── .env                    # Variables d'environnement MongoDB
```

---

## 2. Justification des choix techniques

| Élément         | Justification                                                |
|------------------|-------------------------------------------------------------|
| **Flask**        | Léger, simple à utiliser, idéal pour un prototype pédagogique |
| **MongoDB**      | Adapté au format JSON des logs, et évolutif                 |
| **HMAC-SHA256**  | Garantit l'intégrité des données sans complexité excessive   |
| **Docker**       | Déploiement reproductible et isolé                         |
| **Chart.js**     | Visualisation efficace sans backend complexe                 |
| **dotenv**       | Configuration séparée et versionnable                      |

---

## 3. Requêtes utilisées pour l’analyse

### ➞ Rafales d’échecs en moins de 10 minutes :

```python
pipeline = [
    {"$match": {"status": "failed"}},
    {"$project": {
        "ip": 1,
        "timestamp": {"$dateFromString": {"dateString": "$timestamp"}}
    }},
    {"$group": {
        "_id": {
            "ip": "$ip",
            "minute": {"$dateTrunc": {"date": "$timestamp", "unit": "minute", "binSize": 10}}
        },
        "count": {"$sum": 1}
    }},
    {"$match": {"count": {"$gt": 5}}},
    {"$sort": {"count": -1}}
]
```

### ➞ IPs hors plage autorisée :

```python
for ip in collection.distinct("ip"):
    if not re.match(r"^10\\.0\\.\\d{1,3}\\.\\d{1,3}$", ip):
        print(ip)
```

### ➞ Accès entre 00h–05h UTC :

```python
if 0 <= datetime.fromisoformat(timestamp.replace("Z", "")).hour < 5:
    anomalies.append(ip)
```

---

## 4. Propositions d’amélioration ou d’extension

1. Ajouter une authentification avec rôles pour l'accès à l'interface
2. Ajout de la pagination dans la liste des logs
3. Export des anomalies en CSV ou JSON
4. Intégration d’un service distant (MongoDB Atlas + Render/Fly.io)
5. Intégration Prometheus / Grafana pour les métriques
6. Planification de backup automatique (ex: cron + mongodump)

