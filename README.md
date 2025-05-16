# Système de Journalisation Sécurisée

## Architecture choisie

Le système repose sur une architecture simple, modulaire et sécurisée :


- MongoDB pour stocker les logs au format JSON, localement, avec authentification.


- Python pour l’ingestion des logs, leur hachage (SHA-256) et l’analyse d’anomalies.


- Flask pour créer une interface web de visualisation et une API REST.


- MongoDB Compass pour l’administration manuelle de la base.


- Sauvegardes automatisées avec mongodump + script Python.


L’ensemble est exécuté en local (localhost), sécurisé via l’authentification MongoDB, et facilement portable sur un serveur.
Justification des choix techniques


	 	 	 	 	 	



Requêtes utilisées pour l’analyse


Détection de brute-force (≥5 échecs en 10 min)

```
collection.aggregate([
  {"$match": {"status": "failed"}},
  {"$project": {
	"ip": 1,
	"timestamp": { "$dateFromString": { "dateString": "$timestamp" } }
  }},
  {"$group": {
	"_id": {
  	"ip": "$ip",
  	"minute": { "$dateTrunc": { "date": "$timestamp", "unit": "minute", "binSize": 10 } }
	},
	"count": {"$sum": 1}
  }},
  {"$match": {"count": {"$gt": 5}}},
  {"$sort": {"count": -1}}
])
```

IP hors plage interne autorisée (10.0.x.x)

Filtrage via Python : 
```regex r"^10\.0\.\d{1,3}\.\d{1,3}$"```

Accès entre 00h et 05h UTC (heure suspecte)

Python : ```datetime.fromisoformat(log["timestamp"]).hour < 5```

## Propositions d’amélioration ou d’extension

### Sécurité

Ajouter une signature HMAC pour éviter les altérations même avec accès à la base.


Chiffrer les logs sensibles (ex. IP, utilisateur) avec une clé symétrique stockée ailleurs.


### Déploiement

Conteneuriser l'application avec Docker.


Ajouter une authentification sur l’interface Flask (JWT, login).


### Analyse
Intégrer un mote
ur de corrélation plus puissant (ex : ElasticSearch + Kibana).


Générer des rapports PDF automatiquement des anomalies détectées.


### Machine Learning

Détecter des anomalies comportementales sur base de modèles (profil normal par utilisateur/IP/action).


### Résilience

Mettre en place un système de sauvegarde distant chiffré.


Activer la réplication MongoDB pour tolérance aux pannes.
