# Utilise une image Python officielle
FROM python:3.11-slim

# Définit le dossier de travail
WORKDIR /app

# Copie les fichiers de l'application
COPY . /app

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port de Flask
EXPOSE 5000

# Variable d'environnement pour Flask
ENV FLASK_APP=api.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Commande de lancement
CMD ["flask", "run"]
