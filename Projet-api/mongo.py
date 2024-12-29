import os
import json
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['sncf_data']
collection = db['regularite_mensuelle']

# Chemin vers le répertoire contenant les fichiers JSON
directory = '/Users/sandeep/Desktop/Projet-api/data'

# Parcours des fichiers JSON
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        with open(os.path.join(directory, filename), 'r') as f:
            data = json.load(f)
            # Insérer les données dans MongoDB
            collection.insert_many(data['records'])

# Suppression des fichiers après traitement
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        os.remove(os.path.join(directory, filename))

print("Les données ont été insérées dans MongoDB et les fichiers ont été supprimés.")
