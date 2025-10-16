# dashboard_creuse.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import io
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Immobilier Creuse",
    page_icon="🏡",
    layout="wide"
)

# --- Dictionnaire des principales communes de la Creuse (Code INSEE -> Nom) ---
# NOTE : La Creuse est le département 23, voici quelques-unes de ses communes principales
COMMUNES_CREUSE = {
    "23014": "Aubusson",
    "23019": "Boussac",
    "23031": "Bourganeuf",
    "23034": "Boussac-Bourg",
    "23044": "La Souterraine",
    "23053": "Le Mas-d'Artige",
    "23066": "Saint-Vaury",
    "23096": "Gueret",
    "23102": "Jarnages",
    "23103": "Jarnages",
    "23120": "La Celle-Dunoise",
    "23132": "Moutier-d'Ahun",
    "23138": "Saint-Silvain-sous-Toulx",
    "23144": "Saint-Victor-en-Marche",
    "23154": "Sainte-Feyre",
    "23170": "Vallière",
    "23172": "Ahun",
    "23173": "Ajain",
    "23174": "Alleyrat",
    "23175": "Anzême",
    "23176": "Aubusson",
    "23177": "Azerables",
    "23178": "Bazelat",
    "23179": "Bétête",
    "23180": "Blaudeix",
    "23181": "Le Bourg-d'Hem",
    "23182": "Boussac",
    "23183": "Boussac-Bourg",
    "23184": "Boussacourt",
    "23185": "Brousse",
    "23186": "Bussière-Saint-Georges",
    "23187": "Bussière-Saint-Pierre",
    "23188": "La Celle-Dunoise",
    "23189": "La Celle-sous-Gouzon",
    "23190": "Chambon-sur-Voueize",
    "23191": "Champagnat",
    "23192": "Châtelard",
    "23193": "Le Chauchet",
    "23194": "Chénérailles",
    "23195": "Clugnat",
    "23196": "Cressat",
    "23197": "Croze",
    "23198": "Dompierre-les-Églises",
    "23199": "Dun-le-Palestel",
    "23200": "Fleurat",
    "23201": "Fresselines",
    "23202": "Gartempe",
    "23203": "La Geneytouse",
    "23204": "Gouzon",
    "23205": "Le Grand-Bourg",
    "23206": "Guéret",
    "23207": "Jarnages",
    "23208": "Jarnages",
    "23209": "Jouillat",
    "23210": "Ladapeyre",
    "23211": "Lafat",
    "23212": "Lamarine",
    "23213": "Lépinas",
    "23214": "Lizières",
    "23215": "Lupersat",
    "23216": "Maisonnisses",
    "23217": "Malleret",
    "23218": "Mansat-la-Courrière",
    "23219": "Le Mas-d'Artige",
    "23220": "Moutier-d'Ahun",
    "23221": "La Nouaille",
    "23222": "La Péruse",
    "23223": "Peyrat-la-Nonière",
    "23224": "Pionnat",
    "23225": "Pontarion",
    "23226": "Saint-Avit-de-Tardes",
    "23227": "Saint-Dizier-la-Tour",
    "23228": "Saint-Dizier-les-Domaines",
    "23229": "Saint-Éloi",
    "23230": "Saint-Fiel",
    "23231": "Saint-Georges-la-Pouge",
    "23232": "Saint-Germain-Beaupré",
    "23233": "Saint-Hilaire-la-Palud",
    "23234": "Saint-Hilaire-le-Château",
    "23235": "Saint-Loup",
    "23236": "Saint-Marc-à-Frongier",
    "23237": "Saint-Marc-à-Frongier",
    "23238": "Saint-Martial-le-Mont",
    "23239": "Saint-Martin-Château",
    "23240": "Saint-Michel-de-Veisse",
    "23241": "Saint-Pardoux-les-Cards",
    "23242": "Saint-Priest",
    "23243": "Saint-Priest-la-Feuille",
    "23244": "Saint-Silvain-sous-Toulx",
    "23245": "Saint-Sulpice-le-Dunois",
    "23246": "Saint-Sulpice-le-Guérétois",
    "23247": "Saint-Vaury",
    "23248": "Saint-Victor-en-Marche",
    "23249": "Saint-Yrieix-la-Montagne",
    "23250": "La Souterraine",
    "23251": "Souterrange",
    "23252": "Toulx-Sainte-Croix",
    "23253": "Vallière",
    "23254": "Vareilles",
    "23255": "Le Vigeant",
    "23256": "Viersat",
}

# Inverser le dictionnaire pour avoir Nom -> Code INSEE (plus pratique pour le selectbox)
NOMS_COMMUNES = {v: k for k, v in COMMUNES_CREUSE.items()}

# --- Fonction de chargement des données (générique) ---
@st.cache_data
def load_commune_data(insee_code: str):
    """
    Charge les données DVF 2024 pour une commune de la Creuse donnée par son code INSEE.
    """
    url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/2024/communes/23/{insee_code}.csv"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text), sep=',', low_memory=False)
        
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

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion pour la commune {insee_code} : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
        return pd.DataFrame()

# --- Fonction pour charger toutes les communes de la Creuse ---
@st.cache_data
def load_all_creuse_data():
    """
    Charge les données DVF 2024 pour toutes les communes de la Creuse.
    """
    all_data = []
    
    for insee_code, commune_name in COMMUNES_CREUSE.items():
        df = load_commune_data(insee_code)
        if not df.empty:
            df['commune'] = commune_name
            all_data.append(df)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# --- Interface Utilisateur ---
st.title("🏡 Dashboard Immobilier Creuse")

# Sélection de la commune dans la barre latérale
st.sidebar.header("Sélection de la commune")
selected_commune_name = st.sidebar.selectbox(
    "Choisissez une commune :",
    options=sorted(NOMS_COMMUNES.keys())
)

# Option pour afficher toutes les communes
show_all_communes = st.sidebar.checkbox("Afficher toutes les communes de la Creuse")

# Récupérer le code INSEE correspondant
selected_insee_code = NOMS_COMMUNES[selected_commune_name]

# Afficher un message d'information dynamique
if show_all_communes:
    st.info(f"ℹ️ Données réelles DVF 2024 pour toutes les communes de la **Creuse (département 23)**, provenant de data.gouv.fr")
else:
    st.info(f"ℹ️ Données réelles DVF 2024 pour la commune de **{selected_commune_name}** (INSEE {selected_insee_code}), provenant de data.gouv.fr")

# --- Chargement et Traitement des Données ---
# --- DÉBUT DE LA CORRECTION ---
if show_all_communes:
    df = load_all_creuse_data()
else:
    df = load_commune_data(selected_insee_code)
    # CORRECTION : Ajouter la colonne 'commune' même si on ne charge qu'une seule commune
    if not df.empty:
        df['commune'] = selected_commune_name
# --- FIN DE LA CORRECTION ---

if df.empty:
    if show_all_communes:
        st.warning("Aucune donnée de vente (Maison/Appartement) valide trouvée pour la Creuse en 2024.")
    else:
        st.warning(f"Aucune donnée de vente (Maison/Appartement) valide trouvée pour {selected_commune_name} en 2024.")
    st.stop()

# --- Filtres ---
st.sidebar.header("Filtres")
if show_all_communes:
    communes_disponibles = sorted(df['commune'].unique())
    commune_selectionnee = st.sidebar.multiselect("Commune", communes_disponibles, default=communes_disponibles)
else:
    # Si on n'affiche qu'une commune, on la pré-sélectionne pour le filtre
    commune_selectionnee = [selected_commune_name]

codes_postaux_disponibles = sorted(df['code_postal'].astype(str).unique())
code_postal_selectionne = st.sidebar.multiselect("Code postal", codes_postaux_disponibles, default=codes_postaux_disponibles)
type_local = st.sidebar.selectbox("Type de bien", ['Tous', 'Maison', 'Appartement'])
prix_min = st.sidebar.number_input("Prix minimum (€)", value=0, step=10000)
prix_max = st.sidebar.number_input("Prix maximum (€)", value=int(df['valeur_fonciere'].max()), step=10000)

# Application des filtres
df_filtre = df[
    (df['commune'].isin(commune_selectionnee)) &
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
if show_all_communes:
    st.header("Indicateurs Clés pour la Creuse")
else:
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

if show_all_communes:
    st.header("Visualisations pour la Creuse")
else:
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

if show_all_communes:
    st.subheader("Carte des Transactions dans la Creuse")
else:
    st.subheader(f"Carte des Transactions à {selected_commune_name}")

if 'latitude' in df_filtre.columns and 'longitude' in df_filtre.columns:
    df_carte = df_filtre.sample(min(5000, len(df_filtre)))
    if show_all_communes:
        fig = px.scatter_mapbox(df_carte, lat="latitude", lon="longitude", color="prix_m2", size="surface_reelle_bati", hover_data=["valeur_fonciere", "type_local", "date_mutation", "commune"], color_continuous_scale=px.colors.sequential.Viridis, size_max=15, zoom=8, mapbox_style="open-street-map", title=f"Carte de {len(df_carte)} transactions (échantillon)")
    else:
        fig = px.scatter_mapbox(df_carte, lat="latitude", lon="longitude", color="prix_m2", size="surface_reelle_bati", hover_data=["valeur_fonciere", "type_local", "date_mutation", "commune"], color_continuous_scale=px.colors.sequential.Viridis, size_max=15, zoom=11, mapbox_style="open-street-map", title=f"Carte de {len(df_carte)} transactions (échantillon)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Les données de localisation (latitude/longitude) ne sont pas disponibles pour afficher la carte.")

st.subheader("Détail des Transactions (dernières)")
st.dataframe(df_filtre.sort_values('date_mutation', ascending=False).head(100).drop(columns=['latitude', 'longitude'], errors='ignore'))
