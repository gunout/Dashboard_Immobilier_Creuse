# dashboard_creuse.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Immobilier Creuse",
    page_icon="🏘️",
    layout="wide"
)

# --- Dictionnaire des communes de la Creuse (Code INSEE -> Nom) ---
# NOTE : Pour un usage en production, il faudrait la liste complète des 256 communes.
# Vous pouvez trouver cette liste sur des sites comme data.gouv.fr ou l'INSEE.
# J'inclus ici une liste partielle pour la démonstration.
COMMUNES_CREUSE = {
    "23001": "Ahun",
    "23002": "Azerables",
    "23003": "Bazelat",
    "23004": "Blaudeix",
    "23005": "Le Bourg-d'Hem",
    "23006": "Boussac",
    "23007": "Boussac-Bourg",
    "23008": "Bétête",
    "23009": "La Celle-Dunoise",
    "23010": "La Celle-sous-Gouzon",
    "23011": "Chambon-sur-Voueize",
    "23012": "Champagnat",
    "23013": "Châtelus-le-Marcheix",
    "23014": "Clugnat",
    "23015": "Colondannes",
    "23016": "Crozant",
    "23017": "Dun-le-Palestel",
    "23018": "Fresselines",
    "23019": "Gartempe",
    "23020": "Le Grand-Bourg",
    "23021": "Guéret",
    "23022": "Jarnages",
    "23023": "Lafat",
    "23024": "Ladapeyre",
    "23025": "Lamarine",
    "23026": "La Souterraine",
    "23027": "Lépinas",
    "23028": "Lizières",
    "23029": "Lupersat",
    "23030": "Maison-Feyne",
    "23031": "Malleret-Boussac",
    "23032": "Mansat-la-Courrière",
    "23033": "Marsac",
    "23034": "Masgot",
    "23035": "Maupertuis",
    "23036": "Moutier-d'Ahun",
    "23037": "Peyrabout",
    "23038": "Pontarion",
    "23039": "Saint-Agnant-de-Versillat",
    "23040": "Saint-Éloi",
    "23041": "Saint-Fiel",
    "23042": "Saint-Germain-Beaupré",
    "23043": "Saint-Hilaire-la-Palud",
    "23044": "Saint-Marc-à-Frongier",
    "23045": "Saint-Marien",
    "23046": "Saint-Pardoux-le-Neuf",
    "23047": "Saint-Priest-la-Feuille",
    "23048": "Saint-Silvain-sous-Toulx",
    "23049": "Saint-Sulpice-le-Dunois",
    "23050": "Saint-Vaury",
    "23051": "Saint-Victor-en-Marche",
    "23052": "La Souterraine",
    "23053": "Toulx-Sainte-Croix",
    "23054": "Vallière",
    # ... Ajoutez les autres communes ici
}

# Inverser le dictionnaire pour avoir Nom -> Code INSEE (plus pratique pour le selectbox)
NOMS_COMMUNES = {v: k for k, v in COMMUNES_CREUSE.items()}

# --- Fonction de chargement des données (modifiée pour fichier local) ---
@st.cache_data
def load_all_data():
    """
    Charge toutes les données DVF 2024 depuis le fichier local dvf_2024.csv.
    """
    file_path = "dvf_2024.csv"
    
    try:
        if not os.path.exists(file_path):
            st.error(f"Le fichier {file_path} n'existe pas. Veuillez vous assurer que le fichier est dans le même répertoire que le script.")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path, sep=',', low_memory=False)
        
        if df.empty:
            return pd.DataFrame()

        # Nettoyage (identique à la version précédente)
        df["date_mutation"] = pd.to_datetime(df["date_mutation"], format='%Y-%m-%d', errors='coerce')
        df["valeur_fonciere"] = pd.to_numeric(df["valeur_fonciere"], errors='coerce')
        df = df[df["type_local"].isin(['Maison', 'Appartement'])]
        
        if df.empty:
            return pd.DataFrame()

        df = df.dropna(subset=["valeur_fonciere", "surface_reelle_bati", "code_postal", "date_mutation"])
        df["surface_reelle_bati"] = pd.to_numeric(df["surface_reelle_bati"], errors='coerce')
        df = df.dropna(subset=["surface_reelle_bati"])

        if df.empty:
            return pd.DataFrame()

        df['prix_m2'] = df['valeur_fonciere'] / df['surface_reelle_bati']
        df = df[(df['prix_m2'] > 200) & (df['prix_m2'] < 15000)]
        
        if df.empty:
            return pd.DataFrame()
        
        return df

    except Exception as e:
        st.error(f"Une erreur est survenue lors du chargement des données : {e}")
        return pd.DataFrame()

@st.cache_data
def load_commune_data(insee_code: str, all_data: pd.DataFrame):
    """
    Filtre les données pour une commune donnée par son code INSEE.
    """
    if all_data.empty:
        return pd.DataFrame()
    
    # Filtrer par code INSEE de la commune
    df_commune = all_data[all_data['code_commune'] == insee_code].copy()
    
    return df_commune

# --- Interface Utilisateur ---
st.title("🏘️ Dashboard Immobilier Creuse")

# Sélection de la commune dans la barre latérale
st.sidebar.header("Sélection de la commune")
selected_commune_name = st.sidebar.selectbox(
    "Choisissez une commune :",
    options=sorted(NOMS_COMMUNES.keys())
)

# Récupérer le code INSEE correspondant
selected_insee_code = NOMS_COMMUNES[selected_commune_name]

# Afficher un message d'information dynamique
st.info(f"ℹ️ Données réelles DVF 2024 pour la commune de **{selected_commune_name}** (INSEE {selected_insee_code}), provenant du fichier local dvf_2024.csv")

# --- Chargement et Traitement des Données ---
# Charger toutes les données une seule fois
all_data = load_all_data()

if all_data.empty:
    st.warning("Aucune donnée valide trouvée dans le fichier dvf_2024.csv.")
    st.stop()

# Filtrer pour la commune sélectionnée
df = load_commune_data(selected_insee_code, all_data)

if df.empty:
    st.warning(f"Aucune donnée de vente (Maison/Appartement) valide trouvée pour {selected_commune_name} en 2024.")
    st.stop()

# --- Filtres ---
st.sidebar.header("Filtres")
codes_postaux_disponibles = sorted(df['code_postal'].astype(str).unique())
code_postal_selectionne = st.sidebar.multiselect("Code postal", codes_postaux_disponibles, default=codes_postaux_disponibles)
type_local = st.sidebar.selectbox("Type de bien", ['Tous', 'Maison', 'Appartement'])
prix_min = st.sidebar.number_input("Prix minimum (€)", value=0, step=10000)
prix_max = st.sidebar.number_input("Prix maximum (€)", value=int(df['valeur_fonciere'].max()), step=10000)

# Application des filtres
df_filtre = df[
    (df['code_postal'].astype(str).isin(code_postal_selectionne)) &
    (df['valeur_fonciere'] >= prix_min) &
    (df['valeur_fonciere'] <= prix_max)
].copy()

if type_local != 'Tous':
    df_filtre = df_filtre[df_filtre['type_local'] == type_local]

if df_filtre.empty:
    st.warning("Aucune transaction ne correspond à vos filtres.")
    st.stop()

# --- KPIs et Visualisations ---
st.header(f"Indicateurs Clés pour {selected_commune_name}")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Prix Moyen / m²", f"{df_filtre['prix_m2'].mean():.0f} €")
with col2:
    st.metric("Prix Médian", f"{df_filtre['valeur_fonciere'].median():.0f} €")
with col3:
    st.metric("Transactions", f"{len(df_filtre):,}")
with col4:
    surface_moyenne = df_filtre['surface_reelle_bati'].mean()
    st.metric("Surface Moyenne", f"{surface_moyenne:.0f} m²")

st.header(f"Visualisations pour {selected_commune_name}")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Répartition des Prix au m²")
    fig = px.histogram(df_filtre, x='prix_m2', nbins=50, color='type_local', marginal="box")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Répartition des Types de Biens")
    fig = px.pie(df_filtre, names='type_local', title='Répartition par type')
    st.plotly_chart(fig, use_container_width=True)

st.subheader(f"Carte des Transactions à {selected_commune_name}")
if 'latitude' in df_filtre.columns and 'longitude' in df_filtre.columns:
    df_carte = df_filtre.sample(min(5000, len(df_filtre)))
    fig = px.scatter_mapbox(df_carte, lat="latitude", lon="longitude", color="prix_m2", size="surface_reelle_bati", hover_data=["valeur_fonciere", "type_local", "date_mutation"], color_continuous_scale=px.colors.sequential.Viridis, size_max=15, zoom=11, mapbox_style="open-street-map", title=f"Carte de {len(df_carte)} transactions (échantillon)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Les données de localisation (latitude/longitude) ne sont pas disponibles pour afficher la carte.")

st.subheader("Détail des Transactions (dernières)")
st.dataframe(df_filtre.sort_values('date_mutation', ascending=False).head(100).drop(columns=['latitude', 'longitude'], errors='ignore'))