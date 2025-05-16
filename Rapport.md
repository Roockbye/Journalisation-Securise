# Rapport de Projet : Système de Journalisation Sécurisée

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

C’est le serveur Flask qui définit les routes principales :

- `/` : Accueil

- `/api/logs` : Récupération des logs depuis MongoDB avec filtres éventuels

- `/dashboard` : Accès au tableau de bord visuel

- `/export` : Export de tous les logs au format CSV

Il interagit directement avec :

- `db_connector.py` pour accéder à MongoDB

- Les templates HTML (`home.html`, `api.html`, `dashboard.html`)

- Les modules de détection ou génération de logs pour enrichir la base

Il centralise l'affichage et la logique d’accès aux données.

### db_connector.py 

Ce fichier gère la connexion à la base MongoDB.

- Il utilise le module `pymongo` et charge les variables d’environnement (`.env`) via `dotenv`.

- Il retourne une instance de collection (`secure_logs/logs`) pour réutilisation dans tous les autres scripts.

Utilisé dans presque tous les autres fichiers pour standardiser la connexion MongoDB.

### insert_logs.py 

Génère des logs “normaux” (exemple : connexions réussies/échouées) en JSON pour remplir la base.

- Simule des scénarios classiques d’accès utilisateur (IPs, timestamps, statuts).

- Utilise `hmac` pour signer les logs.

- Appelle `db_connector.py` pour les insérer dans la base.

Utile pour peupler rapidement la base pour les tests ou la démo.

### test_anomaly.py 

Similaire à `insert_logs.py`, mais génère des scénarios anormaux :

- Connexions depuis IPs suspectes

- Activité entre 00h et 05h

- Rafales d’échecs de connexion

Permet de tester les mécanismes de détection d’anomalies manuellement ou via interface.

### anomaly_detection.py

Script CLI d’analyse offline de la base MongoDB :

- Utilise des requêtes d’agrégation MongoDB pour détecter :

    - Rafales d’échecs (pipeline)

    - Accès en heures interdites

    - IPs hors plage

Ne passe pas par Flask : pratique pour des traitements automatisés ou intégration cron.

### backup_mongodb.py

Script pour effectuer un sauvegarde (backup) de la base MongoDB :

- Utilise `subprocess` pour appeler `mongodump`

- Peut être intégré dans une routine cron

Essentiel pour la fiabilité et la résilience du système, dans un cadre professionnel.

### logs_generator.py

Générateur plus générique que `insert_logs.py` :

- Inclus des logs normaux.

- Sert de base pour enrichir le système avec des scénarios plus variés.

Possibilité d’automatiser la génération de flux de logs réalistes sur la durée.

### import_csv.py

Permet d’**importer des logs depuis un fichier CSV** dans MongoDB :

- Convertit les lignes CSV en documents JSON

- Calcule un HMAC à l'import

- Nécessaire pour réintégrer des logs après export ou collecte externe

Utile notamment lors de scénarios Docker avec `/export` → `/import`.

### creation_admin.py

Script pour **créer un compte administrateur par défaut** dans la base :

- Peut être étendu pour un système de gestion de rôles / utilisateurs.

- Recommandé pour sécuriser l’accès à l’interface Flask.

Base pour une future **authentification avec rôles**, mentionnée dans les améliorations.

### templates

Contient les fichiers HTML utilisés par Flask

`home.html`

Page d'accueil simple du site :

- Liens vers les autres fonctionnalités

- Utilise Bootstrap pour le style

`api.html`

Page affichant les logs depuis l’API :

- Interface de filtrage par IP, date, statut

- Appelle `/api/logs` via `fetch()` ou `jQuery.ajax()`

- Représente la vue "utilisateur technique" de l’application

`dashboard.html`

Page du tableau de bord :

- Graphiques via Chart.js :

    - Répartition des statuts (succès/échecs)

    - Heures d’activité

    - Top IPs avec erreurs

- Appelle `/api/logs` en backend

Permet une visualisation synthétique et rapide des activités de sécurité.

## Pourquoi cette séparation des fichiers :

### Respecter le principe de responsabilité unique (SRP)

Chaque fichier a un rôle bien défini, ce qui facilite la lecture, la maintenance et les tests.

### Permettre les tests unitaires et la modularité

On peut tester chaque module séparément

On peut réutiliser les fonctions dans d'autres scripts (par exemple generate_log())

### Favoriser la collaboration

Plusieurs personnes peuvent travailler sur des fichiers différents sans conflits

### Chacun peut se spécialiser sur l’API, la base, les tests, ou l’analyse

Préparer la conteneurisation et le déploiement

Le code est déjà prêt pour être dockerisé

## Schéma visuel

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

## 2. Justification des choix techniques

| Élément         | Justification                                                |
|------------------|-------------------------------------------------------------|
| **Flask**        | Léger, simple à utiliser |
| **MongoDB**      | Adapté au format JSON des logs et évolutif                 |
| **HMAC-SHA256**  | Garantit l'intégrité des données sans complexité excessive   |
| **Docker**       | Déploiement reproductible et isolé                         |
| **Chart.js**     | Visualisation efficace sans backend complexe                 |
| **dotenv**       | Configuration séparée et versionnable                      |


## 3. Requêtes utilisées pour l’analyse

###  Rafales d’échecs en moins de 10 minutes :

```python
db.logs.aggregate([
  { $match: { status: "failed" } },
  {
    $project: {
      ip: 1,
      timestamp: { $dateFromString: { dateString: "$timestamp" } }
    }
  },
  {
    $group: {
      _id: {
        ip: "$ip",
        minute: {
          $dateTrunc: {
            date: "$timestamp",
            unit: "minute",
            binSize: 10
          }
        }
      },
      count: { $sum: 1 }
    }
  },
  { $match: { count: { $gt: 5 } } },
  { $sort: { count: -1 } }
])
```

###  IPs hors plage autorisée :

```python
db.logs.find({
  ip: { $not: { $regex: "^10\\.0\\.\\d{1,3}\\.\\d{1,3}$" } }
})
```

###  Accès entre 00h–05h UTC :

```python
db.logs.aggregate([
  {
    $project: {
      ip: 1,
      timestamp: {
        $dateFromString: { dateString: "$timestamp" }
      },
      hour: {
        $hour: {
          $dateFromString: { dateString: "$timestamp" }
        }
      }
    }
  },
  { $match: { hour: { $lt: 5 } } },
  { $project: { ip: 1, timestamp: 1 } }
])
```


## 4. Propositions d’amélioration ou d’extension

- Ajouter une authentification avec rôles pour l'accès à l'interface
- Ajout de la pagination dans la liste des logs
- Export des anomalies en CSV ou JSON (fait)
- Intégration d’un service distant (MongoDB Atlas + Render/Fly.io)
- Intégration Prometheus / Grafana pour les métriques
- Planification de backup automatique (ex: cron + mongodump)
- Mettre en place de la réplication
- Ajouter un champ confidential_data chiffré avec AES.
- Implémenter un modèle léger (Isolation Forest, K-Means…) pour détecter des anomalies comportementales (nouveaux utilisateurs, horaires inhabituels, séquences anormales…).
- Export des données vers un notebook pour entraînement.
- Utiliser une clé unique par session utilisateur.
- Utiliser watchdog pour surveiller les fichiers en temps réel.

