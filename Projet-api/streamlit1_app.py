import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from pymongo import MongoClient


# Répertoire contenant les fichiers JSON
DATA_DIRECTORY = "/Users/sandeep/Desktop/Projet-api/data"

# MongoDB Connection (Dummy for this example, replace with actual connection if needed)
# client = MongoClient('mongodb://localhost:27017/')
# db = client['sncf_data']
# collection = db['regularite_mensuelle']


def get_latest_file(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError("Aucun fichier JSON trouvé dans le répertoire spécifié.")
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

# Lecture des données depuis le fichier JSON
try:
    latest_file = get_latest_file(DATA_DIRECTORY)
    with open(latest_file, 'r') as file:
        raw_data = json.load(file)
except FileNotFoundError as e:
    st.error(f"Erreur : {e}")
    st.stop()

# Extraction des enregistrements
records = raw_data.get("records", [])
if not records:
    st.error("Aucun enregistrement trouvé dans les données JSON.")
    st.stop()

# Conversion en DataFrame
df = pd.DataFrame([record['fields'] for record in records])

# Nettoyage des colonnes
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

# Transformation de la colonne date
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df['annee'] = df['date'].dt.year
    df['mois'] = df['date'].dt.month
else:
    st.error("La colonne 'date' est introuvable dans les données JSON.")
    st.stop()

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

# Interface Streamlit
st.title("Analyse de la Régularité des TER")

# 1. Top 10 des régions avec le plus de retards et d'annulations
df['retards_et_annulations'] = df['nombre_de_trains_en_retard_a_l_arrivee'] + df['nombre_de_trains_annules']
top_10_regions = df.groupby('region')['retards_et_annulations'].sum().nlargest(10).sort_values(ascending=False)
st.subheader("Top 10 des régions avec le plus de retards et d'annulations")
st.bar_chart(top_10_regions)

# 2. Top 10 des régions avec le moins de retards et d'annulations
bottom_10_regions = df.groupby('region')['retards_et_annulations'].sum().nsmallest(10).sort_values(ascending=False)
st.subheader("Top 10 des régions avec le moins de retards et d'annulations")
st.bar_chart(bottom_10_regions)

# 3. Circulation des trains au fil des années
df_yearly = df.groupby(['annee']).sum(numeric_only=True)
st.subheader("Circulation des trains au fil des années")
st.line_chart(df_yearly[['nombre_de_trains_programmes', 'nombre_de_trains_ayant_circule', 'nombre_de_trains_annules']])

# 4. Analyse des retards en fonction du taux de régularité
st.subheader("Analyse des retards en fonction du taux de régularité")
st.write("Comparaison des retards et annulations en fonction du taux de régularité.")
fig, ax = plt.subplots()
ax.scatter(df['taux_de_regularite'], df['nombre_de_trains_en_retard_a_l_arrivee'], alpha=0.7, label='Retards')
ax.scatter(df['taux_de_regularite'], df['nombre_de_trains_annules'], alpha=0.7, label='Annulations')
ax.set_xlabel('Taux de régularité (%)')
ax.set_ylabel('Nombre de trains')
ax.legend()
st.pyplot(fig)

# 5. Impact des causes spécifiques sur les annulations (groupées par commentaire)
df['causes'] = df['commentaires'].str.extract('(intemperies|travaux|vol|greve|panne)', expand=False).fillna('Autres')
cause_analysis = df[df['causes'] != 'Autres'].groupby('causes')['nombre_de_trains_annules'].sum().sort_values(ascending=False)
st.subheader("Impact des causes spécifiques sur les annulations")
st.bar_chart(cause_analysis)

# 6. Comparaison de la performance annuelle
st.subheader("Comparaison de la performance annuelle")
st.area_chart(df_yearly[['nombre_de_trains_programmes', 'nombre_de_trains_ayant_circule', 'nombre_de_trains_annules']])

# 7. Répartition des retards par région et par mois
heatmap_data = df.pivot_table(index='region', columns='mois', values='nombre_de_trains_en_retard_a_l_arrivee', aggfunc='sum', fill_value=0)
st.subheader("Répartition des retards par région et par mois")
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap='coolwarm', annot=False, cbar=True, ax=ax)
st.pyplot(fig)
