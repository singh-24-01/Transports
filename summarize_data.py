import os
import json
from pymongo import MongoClient
from datetime import datetime

# Répertoire des données
DATA_DIR = "data"

# Connexion MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client.velib
summary_collection = db.summaries
details_collection = db.details

# Lister les fichiers JSON
files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]

if not files:
    print("Aucun fichier à traiter dans le répertoire.")
else:
    for file in files:
        file_path = os.path.join(DATA_DIR, file)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Vérification de la clé 'results'
            results = data.get('results', [])
            if not results:
                print(f"Fichier {file} ne contient pas de données valides ou la clé 'results' est absente.")
                continue

            # Extraire et insérer les données détaillées dans MongoDB
            for record in results:
                details_collection.insert_one(record)

            # Résumer les données (exemple : vélos et stations)
            summary = {
                "file": file,
                "timestamp": datetime.now(),
                "total_stations": len(results),
                "total_bikes_available": sum(
                    r.get('numbikesavailable', 0) for r in results
                ),
                "total_docks_available": sum(
                    r.get('numdocksavailable', 0) for r in results
                )
            }

            # Insérer le résumé dans MongoDB
            summary_collection.insert_one(summary)

            # Supprimer le fichier JSON traité
            os.remove(file_path)
            print(f"Résumé inséré dans MongoDB et fichier supprimé : {file}")

        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON pour le fichier : {file}")
        except Exception as e:
            print(f"Erreur inattendue pour le fichier {file} : {e}")
