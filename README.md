# 🛡️ Système de Journalisation Sécurisée avec Flask & MongoDB

Ce projet est une application pédagogique de journalisation sécurisée en Python, construite avec Flask et MongoDB. Il permet de collecter, stocker, afficher, analyser et exporter des logs de sécurité tout en assurant leur intégrité.

---

## 📦 Fonctionnalités

-  Ingestion de logs au format JSON
-  Hachage d'intégrité (HMAC-SHA256)
-  Stockage NoSQL dans MongoDB
-  Affichage filtrable via interface web (Flask + Bootstrap)
-  Détection d'anomalies :
    - Connexions anormales (heures / IPs)
    - Rafales d'échecs de connexion
-  Export CSV des logs
-  Dashboard avec graphiques (Chart.js)

---

## 🗂 Structure

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

---

## 🚀 Installation & Exécution

### 1. Clone & installe les dépendances
```bash
git clone https://github.com/Roockbye/Journalisation-Securise.git
cd secure-logging-system
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Crée un fichier `.env`
A adapter selon les utilisateurs que vous souhaitez créer
```
MONGO_URI=mongodb://localhost:27017/
MONGO_USER=admin
MONGO_PASS=motdepasse
```

### 3. Lance l'API Flask
```bash
python api.py
```
Accessible sur : [http://localhost:5000](http://localhost:5000)

### 4. (Optionnel) Génére des logs (pour test)
```bash
python insert_logs.py       # Génère des logs "normaux"
python test_anomaly.py      # Génère 3 types d'anomalies
python anomaly_detection.py # Affiche les anomalies en CLI
```
---

## 🐳 Utilisation avec Docker

### 1. Crée un fichier `.env` pour MongoDB
```
MONGO_USER=admin
MONGO_PASS=password
MONGO_URI=mongodb://mongo:27017/
```

### 2. Build & lance les services
Dans un terminal, à la racine du projet :
```bash
docker-compose up --build
```

- Accès API : http://localhost:5000
- MongoDB tourne sur le conteneur `mongo` (port 27017 exposé)

### 3. Insère des logs dans le conteneur (optionnel)
```bash
docker exec -it secure-logging-api python insert_logs.py
```

### 4.Tester l'import CSV manuellement (si tu préfères)

Place secure_logs.logs.csv à la racine du projet

Copie-le dans le conteneur :
```
docker cp secure_logs.logs.csv secure-logging-api:/app/
```
Exécute le script Python d’import  :
```
docker exec -it secure-logging-api python import_csv.py
```

---

## 📊 Dashboard
Accès à `/dashboard` pour visualiser :
- Statuts de logs (succès/échecs)
- Heures d'activité
- Top IPs avec échecs

---

## 📤 Export CSV
Rendez-vous sur `/export` pour télécharger tous les logs au format CSV.

---

## 📚 Objectifs

- Comprendre la journalisation sécurisée
- Manipuler MongoDB & Flask
- Pratiquer l'analyse de logs et détection d'anomalies
- Visualiser les données de sécurité en temps réel

---

## 👩‍💻 Membres du projet



---

## 📜 Licence

Projet libre et open-source dans un but d'apprentissage et de démonstration.