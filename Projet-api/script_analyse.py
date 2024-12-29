#import matplotlib.pyplot as plt
#from pymongo import MongoClient
#from fpdf import FPDF

# Connexion à MongoDB
#client = MongoClient('mongodb://localhost:27017/')
#db = client['sncf_data']
#collection = db['regularite_mensuelle']

# Analyse des données
#data = collection.find()
# Vous pouvez ajouter des opérations d'analyse ici (ex : moyennes, statistiques)

# Création du PDF
#pdf = FPDF()
#pdf.add_page()
#pdf.set_font("Arial", size=12)
#pdf.cell(200, 10, txt="Analyse des données de régularité des TER", ln=True)

# Ajouter des résultats à votre PDF (ex : graphiques, résumés)
#pdf.cell(200, 10, txt="Résultats de l'analyse : ...", ln=True)

# Sauvegarder le PDF
#pdf.output("/Users/nourdaoudi/Desktop/Projet-api/resultats.pdf")

#print("Le fichier PDF a été généré.")

#import os
#import json
#import matplotlib.pyplot as plt
#from pymongo import MongoClient
#from fpdf import FPDF
#import pandas as pd

# Répertoire contenant les fichiers JSON
#DATA_DIRECTORY = "/Users/nourdaoudi/Desktop/Projet-api/data"


# Sauvegarder le PDF
#output_path = "/Users/nourdaoudi/Desktop/Projet-api/resultats.pdf"
#pdf.output(output_path)

#print(f"Le fichier PDF a été généré : {output_path}")






import os
import json
import matplotlib.pyplot as plt
from pymongo import MongoClient
from fpdf import FPDF
import pandas as pd
import seaborn as sns
import streamlit as st

#Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['sncf_data']
collection = db['regularite_mensuelle']

# Analyse des données
data = collection.find()

# Répertoire contenant les fichiers JSON
DATA_DIRECTORY = "/Users/nourdaoudi/Desktop/Projet-api/data"

# Trouver le fichier JSON le plus récent dans le répertoire
def get_latest_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError("Aucun fichier JSON trouvé dans le répertoire spécifié.")
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

try:
    latest_file = get_latest_file(DATA_DIRECTORY)
    print(f"Fichier le plus récent trouvé : {latest_file}")
except FileNotFoundError as e:
    print(e)
    exit(1)

# Lecture des données depuis le fichier JSON
with open(latest_file, 'r') as file:
    raw_data = json.load(file)

# Extraction des enregistrements
records = raw_data.get("records", [])
if not records:
    raise ValueError("Aucun enregistrement trouvé dans les données JSON.")

# Conversion en DataFrame
df = pd.DataFrame([record['fields'] for record in records])

# Nettoyage des colonnes
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

# Transformation de la colonne date
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df['année'] = df['date'].dt.year
    df['mois'] = df['date'].dt.month
else:
    raise KeyError("La colonne 'date' est introuvable dans les données JSON.")

# Assurez-vous que les colonnes sont bien au format numérique
numeric_columns = [
    'nombre_de_trains_programmes',
    'nombre_de_trains_ayant_circule',
    'nombre_de_trains_annules',
    'nombre_de_trains_en_retard_a_l_arrivee',
    'taux_de_regularite',
    'nombre_de_trains_a_l_heure_pour_un_train_en_retard_a_l_arrivee'
]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Création des graphiques
if not os.path.exists("graphs"):
    os.makedirs("graphs")

# 1. Top 10 des régions avec le plus de retards et d'annulations
df['retards_et_annulations'] = df['nombre_de_trains_en_retard_a_l_arrivee'] + df['nombre_de_trains_annules']
top_10_regions = df.groupby('region')['retards_et_annulations'].sum().nlargest(10)
top_10_regions.plot(kind='barh', figsize=(13, 5), color='orange', title='Top 10 des régions avec le plus de retards et d\'annulations')
plt.xlabel('Nombre total')
plt.ylabel('Régions')
plt.savefig("graphs/top_10_retards_annulations.png")
plt.close()

# 2. Top 10 des régions avec le moins de retards et d'annulations
bottom_10_regions = df.groupby('region')['retards_et_annulations'].sum().nsmallest(10)
bottom_10_regions.plot(kind='barh', figsize=(15, 10), color='green', title='Top 10 des régions avec le moins de retards et d\'annulations')
plt.xlabel('Nombre total')
plt.ylabel('Régions')
plt.savefig("graphs/bottom_10_retards_annulations.png")
plt.close()

# 3. Circulation des trains au fil des années
df_yearly = df.groupby(['année']).sum(numeric_only=True)
df_yearly[['nombre_de_trains_programmes', 'nombre_de_trains_ayant_circule', 'nombre_de_trains_annules']].plot(kind='line', figsize=(12, 6), marker='o')
plt.title('Évolution de la circulation des trains au fil des années')
plt.xlabel('Année')
plt.ylabel('Nombre de trains')
plt.legend(['Trains programmés', 'Trains ayant circulé', 'Trains annulés'])
plt.grid()
plt.savefig("graphs/circulation_au_fil_des_annees.png")
plt.close()

# 4. Analyse des retards en fonction du taux de régularité
plt.figure(figsize=(10, 6))
plt.scatter(df['taux_de_regularite'], df['nombre_de_trains_en_retard_a_l_arrivee'], alpha=0.7, label='Retards')
plt.scatter(df['taux_de_regularite'], df['nombre_de_trains_annules'], alpha=0.7, label='Annulations')
plt.title('Analyse des retards en fonction du taux de régularité')
plt.xlabel('Taux de régularité (%)')
plt.ylabel('Nombre de trains')
plt.legend()
plt.grid()
plt.savefig("graphs/retards_vs_regularite.png")
plt.close()

# 5. Impact des causes spécifiques sur les annulations (groupées par commentaire)
df['causes'] = df['commentaires'].str.extract('(intempéries|travaux|vol|grève|panne)', expand=False).fillna('Autres')
cause_analysis = df.groupby('causes')['nombre_de_trains_annules'].sum()
cause_analysis.plot(kind='barh', figsize=(10, 5), color='purple', title='Impact des causes spécifiques sur les annulations')
plt.xlabel('Nombre de trains annulés')
plt.ylabel('Causes')
plt.savefig("graphs/impact_causes_annulations.png")
plt.close()


# 6. Comparaison de la performance annuelle
df_yearly[['nombre_de_trains_programmes', 'nombre_de_trains_ayant_circule', 'nombre_de_trains_annules']].plot(kind='area', stacked=False, alpha=0.5, figsize=(12, 6))
plt.title('Comparaison de la performance annuelle')
plt.xlabel('Année')
plt.ylabel('Nombre de trains')
plt.legend(['Trains programmés', 'Trains ayant circulé', 'Trains annulés'])
plt.savefig("graphs/performance_annuelle.png")
plt.close()

# 7. Répartition des retards par région et par mois
heatmap_data = df.pivot_table(index='region', columns='mois', values='nombre_de_trains_en_retard_a_l_arrivee', aggfunc='sum', fill_value=0)
plt.figure(figsize=(18, 15))
sns.heatmap(heatmap_data, cmap='coolwarm', annot=False, cbar=True)
plt.title('Répartition des retards par région et par mois')
plt.xlabel('Mois')
plt.ylabel('Région')
plt.savefig("graphs/heatmap_retards.png")
plt.close()

# Création du PDF (identique à l'exemple précédent)
from fpdf import FPDF

# Fonction pour nettoyer le texte en remplaçant les caractères non compatibles
def clean_text(text):
    replacements = {
        "’": "'",  # Remplacer l'apostrophe typographique par une apostrophe simple
        "“": '"',  # Remplacer les guillemets typographiques par des guillemets standards
        "”": '"',
        "–": "-",  # Remplacer le tiret long par un tiret simple
        "—": "-",
        "•": "*",  # Remplacer les puces par un astérisque
        "…": "...",  # Remplacer les ellipses typographiques par des points de suspension
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    return text

# Création du PDF avec descriptions détaillées
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=11)


pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, clean_text(
    "Cette analyse présente les données relatives à la régularité des trains express régionaux (TER). "
    "Les informations sont organisées sous différents types de diagrammes permettant d'analyser les retards, "
    "annulations, et les performances globales des TER. Les types de diagrammes utilisés incluent :\n"
    "- Diagrammes en barres horizontales\n"
    "- Graphiques linéaires\n"
    "- Nuages de points\n"
    "- Cartes thermiques\n\n"
    "Ces visualisations permettent d'identifier les régions les plus impactées par les retards et annulations, "
    "de suivre l'évolution de la régularité dans le temps et de comprendre les causes des perturbations."
))
pdf.ln(10)  # Ajout d'un petit espace avant de commencer la suite du document

# Définir les marges (3mm de chaque côté)
pdf.set_left_margin(25)  # Marges gauche
pdf.set_right_margin(25)  # Marges droite

# 1. Top 10 des régions avec le plus de retards et d'annulations
pdf.add_page()
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="1. Top 10 des régions avec le plus de retards et d'annulations", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, 
    clean_text(
        "Description :\n\n"
        "Ce diagramme en barres horizontales montre les 10 régions les plus touchées par les retards et annulations combinés. "
        "Les barres horizontales permettent une meilleure lisibilité des noms de régions. "
        "Les régions avec un plus grand nombre de perturbations sont situées en haut du graphique.\n\n"
        "Utilité :\n\n"
        "- Identifier les zones les plus problématiques pour la régularité des TER.\n"
        "- Prioriser les efforts pour améliorer les performances des régions les plus impactées."
    )
)
pdf.image("graphs/top_10_retards_annulations.png", x=10, y=None, w=180)

# 2. Top 10 des régions avec le moins de retards et d'annulations
pdf.add_page()
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="2. Top 10 des régions avec le moins de retards et d'annulations", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, 
    clean_text(
        "Description :\n\n"
        "Ce diagramme en barres horizontales présente les 10 régions les moins touchées par les retards et annulations combinés. "
        "Il offre une vue comparative des régions où la performance est la meilleure en termes de ponctualité.\n\n"
        "Utilité :\n\n"
        "- Repérer les régions exemplaires qui pourraient servir de modèle pour améliorer les performances ailleurs.\n"
        "- Comprendre les pratiques ou conditions locales favorisant une meilleure régularité."
    )
)
pdf.image("graphs/bottom_10_retards_annulations.png", x=10, y=None, w=180)

# 3. Circulation des trains au fil des années
pdf.add_page()
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="3. Circulation des trains au fil des années", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, 
    clean_text(
        "Description :\n\n"
        "Un graphique linéaire montrant l'évolution des performances des TER par année. "
        "Les lignes incluent :\n"
        "- Nombre de trains programmés.\n"
        "- Nombre de trains ayant circulé.\n"
        "- Nombre de trains annulés.\n\n"
        "Utilité :\n\n"
        "- Suivre les tendances globales des services ferroviaires au fil du temps.\n"
        "- Identifier les années avec des perturbations majeures ou des améliorations notables."
    )
)
pdf.image("graphs/circulation_au_fil_des_annees.png", x=10, y=None, w=180)

# 4. Analyse des retards en fonction du taux de régularité
pdf.add_page()
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="4. Analyse des retards en fonction du taux de régularité", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, 
    clean_text(
        "Description :\n\n"
        "Un nuage de points comparant le taux de régularité avec :\n"
        "- Le nombre de trains en retard.\n"
        "- Le nombre de trains annulés.\n"
        "Chaque point représente une région ou une période.\n\n"
        "Utilité :\n\n"
        "- Identifier les régions où le taux de régularité est fortement influencé par les retards ou les annulations.\n"
        "- Analyser les performances globales en termes de ponctualité."
    )
)
pdf.image("graphs/retards_vs_regularite.png", x=10, y=None, w=180)

# 5. Impact des causes spécifiques sur les annulations
pdf.add_page()
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="5. Impact des causes spécifiques sur les annulations", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, 
    clean_text(
        "Description :\n\n"
        "Ce graphique en barres horizontales montre les principales causes d’annulations identifiées dans les commentaires. "
        "Les causes incluent :\n"
        "- Intempéries.\n"
        "- Travaux.\n"
        "- Vols.\n"
        "- Grèves.\n"
        "- Pannes.\n"
        "- Autres causes.\n\n"
        "Utilité :\n\n"
        "- Identifier les facteurs externes ou internes contribuant aux perturbations.\n"
        "- Planifier des actions correctives en fonction des causes prédominantes."
    )
)
pdf.image("graphs/impact_causes_annulations.png", x=10, y=None, w=180)

# 6. Comparaison de la performance annuelle
pdf.add_page()
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="6. Comparaison de la performance annuelle", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, 
    clean_text(
        "Description :\n\n"
        "Un graphique en aires non empilées montrant l'évolution annuelle des :\n"
        "- Trains programmés.\n"
        "- Trains ayant circulé.\n"
        "- Trains annulés.\n"
        "Le graphique illustre les tendances globales sur une période donnée.\n\n"
        "Utilité :\n\n"
        "- Observer la relation entre les différents indicateurs de performance.\n"
        "- Identifier les années où les perturbations étaient particulièrement importantes."
    )
)
pdf.image("graphs/performance_annuelle.png", x=10, y=None, w=180)

# 7. Répartition des retards par région et par mois
pdf.add_page()
pdf.set_font("Arial", style="B", size=14)
pdf.cell(200, 10, txt="7. Répartition des retards par région et par mois", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, 
    clean_text(
        "Description :\n\n"
        "Une carte thermique (heatmap) illustrant le nombre de retards par région (axe Y) et par mois (axe X). "
        "Les couleurs varient en intensité pour refléter les niveaux de retards.\n\n"
        "Utilité :\n\n"
        "- Identifier les périodes de l'année les plus problématiques.\n"
        "- Analyser les régions les plus affectées pendant certaines saisons."
    )
)
pdf.image("graphs/heatmap_retards.png", x=10, y=None, w=180)

# Sauvegarder le PDF
output_path = "/Users/nourdaoudi/Desktop/Projet-api/resultats.pdf"
pdf.output(output_path)

print(f"Le fichier PDF a été généré : {output_path}")
