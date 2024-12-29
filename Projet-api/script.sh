#!/bin/bash

# URL de l'API
API_URL="https://data.sncf.com/api/records/1.0/search/?dataset=regularite-mensuelle-ter&rows=5000"

# Répertoire où les fichiers seront stockés
DIRECTORY="/Users/sandeep/Desktop/Projet-api/data"

# Crée un nom de fichier avec la date et l'heure
FILENAME="data_$(date +'%Y-%m-%d_%H-%M-%S').json"

# Télécharger les données de l'API et les sauvegarder dans un fichier JSON
curl -s $API_URL -o "$DIRECTORY/$FILENAME"

echo "Les données ont été téléchargées et sauvegardées sous le nom $FILENAME"

