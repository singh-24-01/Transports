import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pymongo import MongoClient
from streamlit_folium import folium_static
import folium
import seaborn as sns
from folium.plugins import MarkerCluster
import json
import os
from branca.colormap import linear

from pymongo import MongoClient

# Connexion à MongoDB Atlas
client = MongoClient("mongodb+srv://lobby:lobby@velib.5muyg.mongodb.net/?retryWrites=true&w=majority&appName=velib")
db = client.velib  # Nom de la base de données
details_collection = db.details  # Collection `details`
summaries_collection = db.summaries  # Collection `summaries`



# Connexion à MongoDB
# client = MongoClient("mongodb://127.0.0.1:27017/")
# db = client.velib
# details_collection = db.details
# summaries_collection = db.summaries

# Charger les données
details_data = pd.DataFrame(list(details_collection.find()))
summaries_data = pd.DataFrame(list(summaries_collection.find()))

# Créer des onglets à gauche
menu = ["Générale", "🚴 Vélib", "🚉 TER", "🏢 Gares"]
choice = st.sidebar.selectbox("Navigation", menu)

# Ajouter une image tout en bas de la barre latérale
st.sidebar.markdown(
    """
    <style>
    .sidebar-bottom {
        position: fixed;
        bottom: 0;
        width: 20%;
        text-align: center;
        padding-bottom: 10px;
    }
    </style>
    <div class="sidebar-bottom">
        <img src="https://cdn.discordapp.com/attachments/1289984168016744570/1322734256354492468/d2b1ffd3-12ef-4527-bca7-b29fba68d356.png?ex=6771f3c5&is=6770a245&hm=7d5bb83609d8a4e0fb6f45f118a0e2e305ec74c536c439fecec0ce7cada24c2e" 
        alt="Logo ou Image" width="200">
        <p style="font-size: 12px; color: #888;">🚀 Connecter les gens, rapprocher les distances</p>
    </div>
    """,
    unsafe_allow_html=True
)


if choice == "Générale":
    st.title("🌟 Tableaux de Bord en Temps Réel pour les Transports")
    st.image(
        "https://cdn.discordapp.com/attachments/1289984168016744570/1322722129313009716/Capture_decran_2024-12-29_a_01.25.01.png?ex=6771e87a&is=677096fa&hm=7e79289fd86db656d3605a2559cce39d082524ed3ee279ba2f4b1edbeff18ed1&", 
        caption="Vue d'ensemble de l'application", 
        use_container_width=True
    )
    
    st.markdown("""
    ### Bienvenue dans le tableau de bord interactif !
    
    Explorez les données et analyses sur les transports en commun en France :
    - 🚴 **Vélib'** : Disponibilité des vélos en temps réel.
    - 🚉 **TER** : Ponctualité et causes des retards par région.
    - 🏢 **Gares** : Localisation et services des gares en France.
    """)
    
    # Bouton pour rediriger vers "🚴 Vélib"
    if st.button("🚀 Utilisez le menu à gauche pour accéder aux différentes sections et commencer votre exploration !"):
        # Mise à jour des paramètres pour rediriger vers "🚴 Vélib"
        st.session_state["Navigation"] = "🚴 Vélib"
        choice = "🚴 Vélib"  # Définit directement le menu comme actif
    # Ajouter un élément stylé en bas
    st.markdown("---")
    st.markdown("""
    ### 🌟 **Citation inspirante**
    > *"La science des données n'est pas seulement des statistiques et du code, c'est aussi de la créativité et du travail d'équipe."*
    """)
    

  # Section des auteurs
    st.markdown("---")
    st.markdown("### ✍️ Auteurs de l'application")
    st.markdown("""
    - 👨‍💻 **NIRMAL Sandeep-Singh**
    - 👩‍💻 **ITAN Chloe**
    - 👩‍💻 **DAOUDI Nour**
    - 👩‍💻 **LOUNISSI Manel**
    """)

    st.markdown("---")
    st.markdown("🎉 Merci d'utiliser notre application, et bonne exploration des données ! 🚀")
    # Ajouter une image tout en bas


elif choice == "🚴 Vélib":
    # Titre de l'application
    st.title("Analyse des disponibilités des vélos Velib - Île-de-France")
# Afficher le logo Île-de-France Mobilités avec le nouveau paramètre
    st.image(
        "https://cdn.discordapp.com/attachments/1290964714670784566/1322552745407807498/Capture_decran_2024-12-28_a_14.12.22.png?ex=67714aba&is=676ff93a&hm=bf924f49a6e3ec4708be76b6040cbaf0185953f19bcb999f67a7b4d73a3f8d92&",
        caption="Île-de-France Mobilités",
        use_container_width=True  # Remplacement du paramètre obsolète
)


    

    # Section : Statistiques globales
    st.header("Statistiques globales")
    if not summaries_data.empty:
        last_summary = summaries_data.iloc[-1]
        st.metric(label="Stations totales", value=last_summary["total_stations"])
        st.metric(label="Vélos disponibles", value=last_summary["total_bikes_available"])
        st.metric(label="Bornes libres", value=last_summary["total_docks_available"])

       

       
    # Section : Disponibilités par type de vélos (mécaniques vs électriques)
    st.header("Histogramme comparant le nombre de vélos mécaniques et électriques")
    if not details_data.empty:
        bike_types = details_data[["mechanical", "ebike"]].sum()
        fig, ax = plt.subplots(figsize=(6, 4))
        bike_types.plot(kind="bar", ax=ax, color=["green", "orange"])
        ax.set_title("Répartition des vélos mécaniques et électriques")
        ax.set_ylabel("Nombre de vélos")
        st.pyplot(fig)
        st.markdown("""  **Analyse** :
- Identifie la répartition entre les deux types.
- Une dominance des vélos mécaniques ou électriques peut refléter une stratégie d'allocation non uniforme. """)
    else:
        st.warning("Aucune donnée disponible pour cette analyse.")

    # Section : Taux d'utilisation des stations
    st.header("Taux d'utilisation des stations")
    if not details_data.empty:
        details_data["usage_rate"] = details_data["numbikesavailable"] / details_data["capacity"] * 100
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(details_data["usage_rate"], bins=20, kde=True, ax=ax, color="blue")
        ax.set_title("Taux d'utilisation des stations")
        ax.set_xlabel("Taux d'utilisation (%)")
        ax.set_ylabel("Nombre de stations")
        st.pyplot(fig)
        st.markdown(""" 
 **Analyse** :
- Met en évidence les stations les plus sollicitées et celles sous-utilisées.
- Une concentration importante autour de taux élevés peut refléter une bonne gestion de la flotte. """)
    else:
        st.warning("Aucune donnée disponible pour cette analyse.")

    # Section : Carte interactive des stations
    st.header("Carte interactive des stations")
    if not details_data.empty:
        # Création de la carte avec Folium
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)  # Coordonnées pour Paris
        for _, station in details_data.iterrows():
            folium.Marker(
                location=[station["coordonnees_geo"]["lat"], station["coordonnees_geo"]["lon"]],
                popup=f"Station : {station['name']}<br>Vélos disponibles : {station['numbikesavailable']}<br>Bornes libres : {station['numdocksavailable']}",
                icon=folium.Icon(color="blue" if station["numbikesavailable"] > 0 else "red")
            ).add_to(m)
        folium_static(m)
        st.markdown(""" 

 **Analyse** :  
- Montre la répartition des stations et leur disponibilité.  
- Met en évidence une forte densité dans les zones centrales (centre de Paris) et une couverture plus limitée en périphérie.  
- Utile pour repérer les zones sous-desservies ou équilibrées en fonction de la demande.""")
    else:
        st.warning("Aucune donnée géographique disponible pour les stations.")

    # Section : Carte interactive avec taux d'utilisation
    st.header("Carte interactive avec taux d'utilisation des stations")
    if not details_data.empty:
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)
        for _, station in details_data.iterrows():
            usage_rate = (station["numbikesavailable"] / station["capacity"] * 100) if station["capacity"] > 0 else 0
            folium.CircleMarker(
                location=[station["coordonnees_geo"]["lat"], station["coordonnees_geo"]["lon"]],
                radius=7,
                color="green" if usage_rate > 50 else "orange" if usage_rate > 25 else "red",
                fill=True,
                fill_opacity=0.6,
                popup=f"""
                <b>Station :</b> {station['name']}<br>
                <b>Taux d'utilisation :</b> {usage_rate:.2f}%<br>
                <b>Vélos disponibles :</b> {station['numbikesavailable']}<br>
                <b>Bornes libres :</b> {station['numdocksavailable']}
                """
            ).add_to(m)
        folium_static(m)
        st.markdown(""" 
**Analyse** :

- Marqueurs verts : Stations avec un taux d'utilisation élevé (bonne disponibilité).
- Marqueurs rouges : Stations sous-desservies ou presque vides, comme celle de Bellefond - Poissonnière avec seulement 11,76 % d'utilisation.
- Marqueurs orange : Indiquent des taux d'utilisation intermédiaires.
- Cette carte permet d'identifier rapidement les stations nécessitant un rééquilibrage en vélos ou en bornes libres. """)
    else:
        st.warning("Aucune donnée disponible pour cette carte.")

    # Section : Top 10 stations avec le plus de vélos disponibles
    st.header("Top 10 des stations avec le plus de vélos disponibles")
    if not details_data.empty:
        top_stations = details_data.nlargest(10, "numbikesavailable")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            x="numbikesavailable", y="name", data=top_stations,
            palette="viridis", ax=ax
        )
        ax.set_title("Top 10 stations avec le plus de vélos disponibles")
        ax.set_xlabel("Nombre de vélos disponibles")
        ax.set_ylabel("Stations")
        st.pyplot(fig)
        st.markdown(""" 
**Analyse** :
- Illustre les stations principales en termes de capacité.
- Ces stations peuvent être stratégiques pour répondre aux pics de demande. """)
    else:
        st.warning("Aucune donnée disponible pour cette analyse.")

    # Section : Heatmap des vélos disponibles par arrondissement
    st.header("Heatmap des vélos disponibles par arrondissement")
    if not details_data.empty:
        bikes_by_arrondissement = details_data.groupby("nom_arrondissement_communes")["numbikesavailable"].sum().reset_index()
        bikes_by_arrondissement.columns = ["Arrondissement", "Vélos disponibles"]
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(
            bikes_by_arrondissement.pivot_table(index="Arrondissement", values="Vélos disponibles"),
            annot=True, fmt=".0f", cmap="coolwarm", cbar=True, ax=ax
        )
        ax.set_title("Disponibilité des vélos par arrondissement")
        st.pyplot(fig)
        st.markdown(""" 
**Analyse** :
- Offre une vue détaillée sur la distribution des vélos.
- Idéal pour identifier les disparités entre arrondissements. """)
    else:
        st.warning("Aucune donnée disponible pour cette analyse.")

    # Section : Comparaison vélos mécaniques vs électriques par arrondissement
    st.header("Comparaison vélos mécaniques vs électriques par arrondissement")
    if not details_data.empty:
        bike_comparison = details_data.groupby("nom_arrondissement_communes")[["mechanical", "ebike"]].sum()
        fig, ax = plt.subplots(figsize=(10, 6))
        bike_comparison.plot(kind="bar", stacked=True, ax=ax, color=["green", "orange"])
        ax.set_title("Comparaison des vélos mécaniques et électriques par arrondissement")
        ax.set_ylabel("Nombre de vélos")
        ax.set_xlabel("Arrondissements")
        st.pyplot(fig)
        st.markdown("""**Analyse** : 
- Montre une répartition détaillée des ressources par zone.
- Une forte disparité pourrait indiquer des ajustements nécessaires dans la distribution. """)
    else:
        st.warning("Aucune donnée disponible pour cette analyse.")

    # Section : Carte des stations sous-desservies
    st.header("Carte des stations sous-desservies (taux d'utilisation < 20%)")
    if not details_data.empty:
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)
        for _, station in details_data.iterrows():
            usage_rate = (station["numbikesavailable"] / station["capacity"] * 100) if station["capacity"] > 0 else 0
            if usage_rate < 20:  # Filtrer les stations avec un faible taux d'utilisation
                folium.Marker(
                    location=[station["coordonnees_geo"]["lat"], station["coordonnees_geo"]["lon"]],
                    popup=f"""
                    <b>Station :</b> {station['name']}<br>
                    <b>Taux d'utilisation :</b> {usage_rate:.2f}%<br>
                    <b>Vélos disponibles :</b> {station['numbikesavailable']}
                    """,
                    icon=folium.Icon(color="red")
                ).add_to(m)
        folium_static(m)
        st.markdown("""
**Analyse** :
- Permet d'identifier les zones où les vélos ne sont pas suffisamment utilisés.
- Ces données sont cruciales pour repositionner les stations ou adapter les flottes. """)
    else:
        st.warning("Aucune donnée disponible pour cette carte.")

    # Section : Carte avec clusterisation des stations
    st.header("Carte avec clusterisation des stations")
    if not details_data.empty:
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(m)
        for _, station in details_data.iterrows():
            folium.Marker(
                location=[station["coordonnees_geo"]["lat"], station["coordonnees_geo"]["lon"]],
                popup=f"""
                <b>Station :</b> {station['name']}<br>
                <b>Vélos disponibles :</b> {station['numbikesavailable']}<br>
                <b>Bornes libres :</b> {station['numdocksavailable']}
                """
            ).add_to(marker_cluster)
        folium_static(m)
        st.markdown(""" 
**Analyse** :
- Simplifie la visualisation des stations lorsqu'elles sont nombreuses.
- Utile pour une analyse régionale rapide des zones à forte densité. """)
    else:
        st.warning("Aucune donnée disponible pour cette carte.")

elif choice == "🚉 TER":
    st.title("Analyse de la Régularité des TER")

    # Chemin des fichiers JSON
    DATA_DIRECTORY = "/Users/sandeep/Desktop/Transport/data/dataTER"

    def get_latest_file(directory):
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".json")]
        if not files:
            raise FileNotFoundError("Aucun fichier JSON trouvé dans le répertoire spécifié.")
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    try:
        latest_file = get_latest_file(DATA_DIRECTORY)
        with open(latest_file, 'r') as file:
            raw_data = json.load(file)
    except FileNotFoundError as e:
        st.error(f"Erreur : {e}")
        st.stop()

    records = raw_data.get("records", [])
    if not records:
        st.error("Aucun enregistrement trouvé dans les données JSON.")
        st.stop()

    df = pd.DataFrame([record['fields'] for record in records])
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['annee'] = df['date'].dt.year
        df['mois'] = df['date'].dt.month
    else:
        st.error("La colonne 'date' est introuvable dans les données JSON.")
        st.stop()

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


elif choice == "🏢 Gares":
    st.title("Carte des Gares SNCF")

    # Chemin vers le répertoire contenant les fichiers JSON
    data_directory = "/Users/sandeep/Desktop/Transport/data/dataa"

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
                # Nous gérons ici les segments multiples (séparés par ;)
                segments = fields.get("segment_drg", "N/A").split(";")
                for segment in segments:
                    stations.append({
                        "nom": fields.get("nom", "N/A"),
                        "latitude": fields["position_geographique"][0],
                        "longitude": fields["position_geographique"][1],
                        "segment_drg": segment.strip(),  # Suppression des espaces éventuels
                    })
        return pd.DataFrame(stations)

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
        folium_static(m)
    else:
        st.info("Aucun fichier JSON trouvé dans le répertoire spécifié.")


