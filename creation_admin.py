from pymongo import MongoClient
from pymongo.errors import OperationFailure
import getpass

# Connexion MongoDB sans authentification (attention : seulement tant que la sécurité n'est pas activée)
client = MongoClient("mongodb://localhost:27017/")
admin_db = client["admin"]

def create_admin_user():
    print("Création d'un compte administrateur MongoDB")
    
    username = input("Nom d'utilisateur admin à créer : ").strip()
    password = getpass.getpass("Mot de passe pour l'utilisateur : ").strip()

    try:
        admin_db.command("createUser", username,
                         pwd=password,
                         roles=[
                             {"role": "userAdminAnyDatabase", "db": "admin"},
                             {"role": "readWriteAnyDatabase", "db": "admin"}
                         ])
        print(f"Utilisateur '{username}' créé avec succès.")
    except OperationFailure as e:
        print(f"Erreur lors de la création de l'utilisateur : {e}")

if __name__ == "__main__":
    create_admin_user()
