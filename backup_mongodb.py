import os
import subprocess
from datetime import datetime, timedelta
import argparse

MONGO_DB = "secure_logs"
MONGO_USER = "admin"
MONGO_PWD = "password"
MONGO_HOST = "localhost"
BACKUP_DIR = "/home/rocky/Documents/MongoDB/mongo_backups"
DAYS_TO_KEEP = 35

def create_backup():
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(BACKUP_DIR, today)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print(f"Sauvegarde de la base '{MONGO_DB}' vers : {output_path}")

    command = [
        "mongodump",
        f"--db={MONGO_DB}",
        f"--username={MONGO_USER}",
        f"--password={MONGO_PWD}",
        f"--authenticationDatabase=admin",
        f"--host={MONGO_HOST}",
        f"--out={output_path}"
    ]

    try:
        subprocess.run(command, check=True)
        print("Sauvegarde terminée avec succès.")
    except subprocess.CalledProcessError as e:
        print("Erreur lors de la sauvegarde :", e)

def clean_old_backups():
    print(f"Suppression des sauvegardes de plus de {DAYS_TO_KEEP} jours...")
    cutoff_date = datetime.now() - timedelta(days=DAYS_TO_KEEP)

    for folder in os.listdir(BACKUP_DIR):
        try:
            folder_date = datetime.strptime(folder, "%Y-%m-%d")
            full_path = os.path.join(BACKUP_DIR, folder)
            if folder_date < cutoff_date:
                subprocess.run(["rm", "-rf", full_path])
                print(f"Supprimé : {folder}")
        except ValueError:
            continue  # Ignore les noms qui ne sont pas des dates

def restore_backup(date):
    backup_path = os.path.join(BACKUP_DIR, date, MONGO_DB)
    
    if not os.path.exists(backup_path):
        print(f"Aucune sauvegarde trouvée pour {date} à l’emplacement : {backup_path}")
        return

    print(f"Restauration depuis : {backup_path}")

    command = [
        "mongorestore",
        f"--db={MONGO_DB}",
        f"--username={MONGO_USER}",
        f"--password={MONGO_PWD}",
        f"--authenticationDatabase=admin",
        f"--host={MONGO_HOST}",
        "--drop",  # Supprime la base existante avant de restaurer
        backup_path
    ]

    try:
        subprocess.run(command, check=True)
        print("Restauration terminée avec succès.")
    except subprocess.CalledProcessError as e:
        print("Erreur lors de la restauration :", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sauvegarde ou restauration MongoDB")
    parser.add_argument("--backup", action="store_true", help="Créer une sauvegarde")
    parser.add_argument("--restore", metavar="YYYY-MM-DD", help="Restaurer une sauvegarde d'une date donnée")
    parser.add_argument("--clean", action="store_true", help="Supprimer les anciennes sauvegardes")
    args = parser.parse_args()

    if args.backup:
        create_backup()
    if args.clean:
        clean_old_backups()
    if args.restore:
        restore_backup(args.restore)
    if not (args.backup or args.clean or args.restore):
        parser.print_help()

#commandes
#python3 backup_mongodb.py --backup
#python3 backup_mongodb.py --restore YYYY-MM-DD
#python3 backup_mongodb.py --clean
#python3 backup_mongodb.py --backup --clean

#python3 backup_mongodb.py --restore YYYY-MM-DD --backup
#python3 backup_mongodb.py --restore YYYY-MM-DD --clean
#python3 backup_mongodb.py --backup --restore YYYY-MM-DD
#python3 backup_mongodb.py --backup --clean --restore YYYY-MM-DD
#python3 backup_mongodb.py --backup --restore YYYY-MM-DD --clean
#python3 backup_mongodb.py --restore YYYY-MM-DD --backup --clean
#python3 backup_mongodb.py --backup --clean --restore YYYY-MM-DD
#python3 backup_mongodb.py --restore YYYY-MM-DD --backup --clean
