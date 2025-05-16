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
├── backup_mongodb.py       # Backup des logs
├── logs_generator.py
├── import_csv.py           # Mettre en place le CSV de mongodb (docker file)
├── creation_admin.py   
├── templates/              # Templates HTML (Flask)
│   ├── home.html
│   ├── api.html
│   └── dashboard.html
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env                    # Variables d'environnement MongoDB
└── README.md
```
### api.py 

### db_connector.py 

### insert_logs.py 

### test_anomaly.py 

### anomaly_detection.py

### backup_mongodb.py

### logs_generator.py

### import_csv.py

### creation_admin.py

### templates

- home.html

- api.html

- dashboard.html


```
                          ┌─────────────────────────────┐
                          │        Interface Flask       │
                          │     (api.py + templates)     │
                          │          port 5000           │
                          └──────────────┬───────────────┘
                                         │
                                         ▼
                   Utilisateur ←→ [Filtrage / Dashboard / Export CSV]

                                         │
                                         ▼
                   ┌─────────────────────────────┐
                   │         MongoDB             │
                   │    (localhost:27017 ou      │
                   │     service Docker mongo)   │
                   └──────────────┬──────────────┘
                                  │
          ┌───────────────────────┴────────────────────────────┐
          │                                                    │
          ▼                                                    ▼

 [insert_logs.py]                                    [test_anomaly.py]
 Génère des logs valides                            Génère des logs anormaux

          ▼                                                    ▼

                ┌───────────────────────────────┐
                │  Collection : secure_logs.logs │
                └──────────────┬────────────────┘
                               │
                               ▼

        ┌────────────────────────────────────────────────────┐
        │ Scripts d’analyse offline                          │
        │  ├── anomaly_detection.py  ← détection manuelle     │
        │  └── integrity_check.py     ← vérifie les HMAC      │
        └────────────────────────────────────────────────────┘
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

