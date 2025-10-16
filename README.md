# Dashboard_Immobilier_Creuse
🏘️ Dashboard Immobilier Creuse  ℹ️ Données réelles DVF 2024 pour la commune de Fresselines (INSEE 23018), provenant du fichier local dvf_2024.csv

# EXAMPLE
<img width="1280" height="1024" alt="Screenshot_2025-10-16_23-11-46" src="https://github.com/user-attachments/assets/51b310dd-3d7a-40c7-8fb8-381b8d705a56" />
<img width="1280" height="1024" alt="Screenshot_2025-10-16_23-11-53" src="https://github.com/user-attachments/assets/c56c5722-18af-4621-9e53-68e9dd185b51" />

# METHODE LOCAL ( FICHIER LOCAL )
# TÉLÉCHARGEMENT " dvf_2024.csv " avec CURL

    curl -L -o dvf_2024.csv.gz "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/full.csv.gz"

# RUN PROGRAM ( CREUSE - 53 Communes ) METHODE LOCAL

    streamlit run Dash.py

PS : pour la methode local s'assurer d'avoir le fichier : dvf_2024.csv dans le meme dossier que Dash.py
