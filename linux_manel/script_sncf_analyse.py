import os
import json
import pandas as pd
import folium
from branca.colormap import linear
from fpdf import FPDF

# Chemin vers le répertoire contenant les fichiers JSON
data_directory = "/Users/nourdaoudi/Desktop/linux_manel/data"

import os
import json
import pandas as pd
import folium
from fpdf import FPDF
from branca.colormap import linear

# Chemins des répertoires
data_directory = "/Users/nourdaoudi/Desktop/linux_manel/data"
output_directory = "/Users/nourdaoudi/Desktop/linux_manel/graphes"
pdf_output_path = "/Users/nourdaoudi/Desktop/linux_manel/report.pdf"

# Créer le répertoire pour les graphes si inexistant
os.makedirs(output_directory, exist_ok=True)

# Charger les données JSON les plus récentes
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
            segment_drg = fields.get("segment_drg", "N/A")
            # Gestion des segments multiples
            expanded_segments = segment_drg.split(";")
            for segment in expanded_segments:
                stations.append({
                    "nom": fields.get("nom", "N/A"),
                    "latitude": fields["position_geographique"][0],
                    "longitude": fields["position_geographique"][1],
                    "segment_drg": segment.strip(),
                    "frequence": fields.get("frequence", 0)  # Ajouter une fréquence fictive si non fournie
                })
    return pd.DataFrame(stations)

# Générer une carte Folium et la sauvegarder
def generate_map(df, filter_column, filter_value, output_file, colormap):
    m = folium.Map(location=[47, 2], zoom_start=6, tiles="CartoDB positron")

    # Filtrer les données
    filtered_df = df if filter_value == "Tous" else df[df[filter_column] == filter_value]

    for _, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            color=colormap(row["frequence"]),
            fill=True,
            fill_color=colormap(row["frequence"]),
            fill_opacity=0.7,
            popup=f"Nom: {row['nom']}<br>Segment: {row['segment_drg']}<br>Fréquence: {row['frequence']}"
        ).add_to(m)

    m.save(output_file)

# Générer un PDF avec les images
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Rapport des Cartes des Gares SNCF', align='C', ln=True)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_map_image(self, image_path, title):
        self.add_page()
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, ln=True, align='C')
        self.ln(10)
        self.image(image_path, x=10, y=30, w=190)

# Main
if __name__ == "__main__":
    data = load_latest_data(data_directory)

    if data is None:
        print("Aucun fichier JSON trouvé dans le répertoire spécifié.")
    else:
        stations_df = extract_station_data(data)

        # Définir le colormap
        colormap = linear.RdYlGn.scale(stations_df["frequence"].min(), stations_df["frequence"].max())
        colormap.caption = "Fréquence des gares"

        # Générer les cartes pour chaque type de filtre
        filters = ["Tous", "A", "B", "C"]
        images = []

        for filter_value in filters:
            output_file = os.path.join(output_directory, f"map_{filter_value}.html")
            generate_map(stations_df, "segment_drg", filter_value, output_file, colormap)

            # Convertir la carte HTML en image (si nécessaire, utiliser selenium ou une capture d'écran)
            image_path = os.path.join(output_directory, f"map_{filter_value}.png")
            os.system(f"webkit2png {output_file} -o {image_path}")  # Exemple, ajustez selon vos outils disponibles
            images.append((image_path, f"Carte pour le segment {filter_value}"))

        # Créer un PDF avec les cartes
        pdf = PDF()

        for image_path, title in images:
            if os.path.exists(image_path):
                pdf.add_map_image(image_path, title)

        pdf.output(pdf_output_path)
        print(f"Rapport PDF généré : {pdf_output_path}")
