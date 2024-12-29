from pymongo import MongoClient
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os

# Connexion à MongoDB
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client.idfm
collection = db.details

# Charger les données depuis MongoDB
data = pd.DataFrame(list(collection.find()))

# Vérifier si des données existent
if data.empty:
    print("Aucune donnée disponible dans MongoDB.")
    exit()

# Créer un PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Titre du PDF
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="Analyse des données Île-de-France Mobilités", ln=True, align='C')
pdf.ln(10)  # Ajouter un espace

# Sous-titre
pdf.set_font("Arial", style="B", size=12)
pdf.cell(200, 10, txt=f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
pdf.ln(10)

# Préparer les données
data['theme'] = data['metas'].apply(lambda x: x.get('theme', ['Inconnu'])[0])
data['records_count'] = data['metas'].apply(lambda x: x.get('records_count', 0))
data['territory'] = data['metas'].apply(lambda x: x.get('territory', ['Inconnu'])[0])

# **1. Barplot : Nombre de jeux de données par thème**
if 'theme' in data.columns:
    plt.figure(figsize=(8, 6))
    theme_counts = data['theme'].value_counts()
    theme_counts.plot(kind='bar', color='skyblue')
    plt.title("Nombre de jeux de données par thème")
    plt.xlabel("Thème")
    plt.ylabel("Nombre de jeux de données")
    plt.xticks(rotation=45, ha='right')
    barplot_path = "barplot_theme.png"
    plt.tight_layout()
    plt.savefig(barplot_path)
    plt.close()

    # Ajouter le barplot au PDF
    pdf.add_page()
    pdf.cell(200, 10, txt="Barplot : Nombre de jeux de données par thème", ln=True, align='C')
    pdf.ln(5)
    pdf.image(barplot_path, x=10, y=30, w=190)
    os.remove(barplot_path)

# **2. Pie Chart : Répartition des thèmes**
if 'theme' in data.columns:
    theme_counts = data['theme'].value_counts()
    plt.figure(figsize=(8, 6))
    theme_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Répartition des thèmes")
    piechart_theme_path = "piechart_theme.png"
    plt.tight_layout()
    plt.savefig(piechart_theme_path)
    plt.close()

    # Ajouter le pie chart au PDF
    pdf.add_page()
    pdf.cell(200, 10, txt="Pie Chart : Répartition des thèmes", ln=True, align='C')
    pdf.ln(5)
    pdf.image(piechart_theme_path, x=10, y=30, w=190)
    os.remove(piechart_theme_path)

# **3. Pie Chart : Répartition des territoires**
if 'territory' in data.columns:
    territory_counts = data['territory'].value_counts()
    plt.figure(figsize=(8, 6))
    territory_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Répartition des territoires")
    piechart_territory_path = "piechart_territory.png"
    plt.tight_layout()
    plt.savefig(piechart_territory_path)
    plt.close()

    # Ajouter le pie chart au PDF
    pdf.add_page()
    pdf.cell(200, 10, txt="Pie Chart : Répartition des territoires", ln=True, align='C')
    pdf.ln(5)
    pdf.image(piechart_territory_path, x=10, y=30, w=190)
    os.remove(piechart_territory_path)

# **4. Histogramme : Distribution des enregistrements (records_count)**
if 'records_count' in data.columns:
    plt.figure(figsize=(8, 6))
    data['records_count'].plot(kind='hist', bins=10, color='coral', edgecolor='black')
    plt.title("Distribution du nombre d'enregistrements")
    plt.xlabel("Nombre d'enregistrements")
    plt.ylabel("Fréquence")
    hist_path = "histogram_records.png"
    plt.tight_layout()
    plt.savefig(hist_path)
    plt.close()

    # Ajouter l'histogramme au PDF
    pdf.add_page()
    pdf.cell(200, 10, txt="Histogramme : Distribution du nombre d'enregistrements", ln=True, align='C')
    pdf.ln(5)
    pdf.image(hist_path, x=10, y=30, w=190)
    os.remove(hist_path)

# **5. Tableau des jeux de données les plus grands**
pdf.add_page()
pdf.cell(200, 10, txt="Tableau des plus grands jeux de données", ln=True, align='C')
pdf.ln(10)
top_datasets = data.nlargest(5, 'records_count')[['theme', 'records_count']]
for index, row in top_datasets.iterrows():
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt=f"Thème : {row['theme']}\nNombre d'enregistrements : {row['records_count']}\n")
    pdf.ln(5)

# Enregistrer le PDF
output_file = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
pdf.output(output_file)

print(f"PDF généré : {output_file}")
