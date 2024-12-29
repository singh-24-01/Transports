from pymongo import MongoClient

# Connexion à MongoDB (par défaut, localhost:27017)
client = MongoClient('mongodb://localhost:27017/')

# Accéder à une base de données
db = client.test_database

# Créer une collection
collection = db.test_collection

# Insérer un document de test
collection.insert_one({"name": "test", "value": 1})

# Vérifier si l'insertion a bien fonctionné
document = collection.find_one({"name": "test"})
print(document)
