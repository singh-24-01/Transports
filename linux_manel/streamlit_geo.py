
import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
import os
from branca.colormap import linear

# Chemin vers le répertoire contenant les fichiers JSON
data_directory = "/Users/sandeep/Desktop/linux_manel/data"

# Charger les données JSON les plus récentes
@st.cache_data
def load_latest_data(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    if not files:
        return None
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))
    with open(os.path.join(directory, latest_file), "r") as f:
        data = json.load(f)
    return data

# Extraire les informations nécessaires des données JSON
def extract_station_data(data):
    stations = []
    for record in data.get("records", []):
        fields = record.get("fields", {})
        if "position_geographique" in fields:
            # Nous gérons ici les segments multiples (séparés par des ;)
            segments = fields.get("segment_drg", "N/A").split(";")
            for segment in segments:
                stations.append({
                    "nom": fields.get("nom", "N/A"),
                    "latitude": fields["position_geographique"][0],
                    "longitude": fields["position_geographique"][1],
                    "segment_drg": segment.strip(),  # Suppression des espaces éventuels
                })
    return pd.DataFrame(stations)

# Interface Streamlit
st.title("Carte des Gares SNCF")

st.header("Description des Données")
st.subheader("Problématique")
st.write("Comment visualiser et analyser efficacement les données géographiques et segmentaires des gares SNCF pour améliorer la compréhension des réseaux ferroviaires et faciliter les prises de décision?")

st.subheader("Contexte")
st.write("Les gares SNCF jouent un rôle crucial dans l'interconnexion des villes et des trains. Ce jeu de données représente l'ensemble des gares répondant à la définition fournie par SNCF Gares & Connexions, en incluant des informations géographiques et administratives pertinentes pour une gestion optimale des infrastructures.")

st.subheader("Objectifs")
st.write("1. Visualiser la position géographique des gares sur une carte interactive.\n2. Permettre le filtrage des données par segment pour une analyse ciblée.\n3. Fournir une interface utilisateur intuitive pour explorer les détails des gares et leurs fréquences d'utilisation.")

# Charger les données depuis le répertoire
data = load_latest_data(data_directory)

# Définir les descriptions des segments
def get_segment_description(segment):
    descriptions = {
        "A": "Secteur A : pourrait correspondre à un réseau ou à une ligne majeure (par ex., Paris – Lyon).",
        "B": "Secteur B : une autre ligne ou un autre groupe de gares dans la même région.",
        "C": "Secteur C : correspond à des gares locales ou régionales.",
        "D": "Secteur D : correspond à des gares moins fréquentées ou éloignées.",
    }
    return descriptions.get(segment, "Segment inconnu")

if data is not None:
    stations_df = extract_station_data(data)

    # Ajouter un filtre pour les segments
    segments = stations_df["segment_drg"].unique().tolist()
    selected_segment = st.selectbox("Filtrer par type de segment", options=["Tous"] + segments, format_func=lambda x: "Tous" if x == "Tous" else f"{x}: {get_segment_description(x)}")

    # Filtrer les données en fonction du segment sélectionné
    if selected_segment != "Tous":
        stations_df = stations_df[stations_df["segment_drg"] == selected_segment]

    # Afficher le DataFrame dans Streamlit
    st.subheader("Tableau des Gares")
    st.dataframe(stations_df)

    # Créer une carte Folium
    st.subheader("Carte des Gares")
    m = folium.Map(location=[47, 2], zoom_start=6)  # Centré sur la France

    # Définir la palette de couleurs pour le dégradé (du rouge au vert)
    colormap = linear.RdYlGn_09.scale(0, len(segments))  # Palette de couleurs allant de rouge à vert
    segment_to_color = {segment: colormap(i) for i, segment in enumerate(segments)}

    # Ajouter les gares à la carte avec un dégradé de couleur selon le segment
    for _, row in stations_df.iterrows():
        color = segment_to_color.get(row["segment_drg"], "#000000")  # Noir par défaut si le segment est inconnu
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            popup=f"Nom: {row['nom']}<br>Segment: {row['segment_drg']}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)

    # Afficher la carte dans Streamlit
    st_folium(m, width=700, height=500)
else:
    st.info("Aucun fichier JSON trouvé dans le répertoire spécifié.")