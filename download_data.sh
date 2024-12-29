#!/bin/bash

# Répertoire pour stocker les données
DATA_DIR="data"
mkdir -p $DATA_DIR

# URL de l'API
API_URL="https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=100&lang=fr"

# Nom du fichier avec horodatage
FILE_NAME="$DATA_DIR/velib_$(date +%Y%m%d_%H%M%S).json"

# Télécharger les données
curl -s "$API_URL" -o "$FILE_NAME"

if [ $? -eq 0 ]; then
    echo "Données téléchargées avec succès : $FILE_NAME"
else
    echo "Erreur lors du téléchargement des données."
fi
