# JobPulse

Plateforme de collecte et d'analyse d'offres d'emploi, construite avec Python et Apache Spark (projet de fin d'etudes, sujet : conception d'une plateforme Big Data de collecte et d'analyse des offres d'emploi).

## Presentation

JobPulse collecte des offres d'emploi via des API publiques, les nettoie, en extrait les competences demandees, puis les agrege dans des tables prêtes pour un tableau de bord. L'architecture est modulaire : une nouvelle source de donnees s'ajoute sans modifier le reste du pipeline.

## Architecture

Le pipeline suit une architecture en trois couches (medallion) :

| Couche | Contenu | Emplacement |
|---|---|---|
| Bronze | Reponses brutes des API, une collecte par jour | data/bronze/AAAA-MM-JJ/ |
| Silver | Offres dedoublonnees et nettoyees, competences extraites (Parquet) | data/silver/ |
| Gold | Tables d'agregation pour le tableau de bord (Parquet) | data/gold/ |

Flux : API, Bronze, Silver (Spark), Gold (Spark), tableau de bord Streamlit.

## Sources de donnees

- **La bonne alternance** (API Recherche d'opportunites d'emploi en alternance) : source principale, integree au pipeline modulaire.
- **France Travail** : scripts de collecte du referentiel ROME 4.0 (competences) et des statistiques du marche du travail (src/competences_rome.py, src/marche_travail.py). Ils ne sont pas encore integres au pipeline modulaire.

Les donnees de La bonne alternance sont reservees a un usage non lucratif.

## Installation

Prerequis : Python 3.12 et Java 21 (necessaire a Spark).

    uv venv --python 3.12 .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt

Creer un fichier .env a la racine (ignore par Git) avec la cle d'API :

    LBA_API_KEY=votre_cle

## Utilisation

    python src/pipeline.py             # collecte (couche Bronze)
    python src/silver_offres.py        # nettoyage et dedoublonnage
    python src/silver_competences.py   # extraction des competences
    python src/gold.py                 # tables d'agregation
    streamlit run src/dashboard.py     # tableau de bord

Le tableau de bord est optionnel : les tables Gold sont des fichiers Parquet lisibles directement avec pandas.

## Tests

    python -m pytest tests/ -v

Les tests couvrent l'extraction des competences (tests unitaires) et la qualite des donnees : pas de doublons, identifiants renseignes, coherence des totaux entre Silver et Gold.

## Ajouter une source

1. Creer src/sources/nom_de_la_source.py avec une fonction collecter(config, dossier) qui ecrit ses fichiers JSON dans le dossier donne et renvoie le nombre d'offres collectees.
2. Declarer la source dans src/config.py (cle "actif" a True) : src/pipeline.py la lance automatiquement.

## Limites connues

- Echantillon reduit : 43 offres distinctes apres deux jours de collecte. Les resultats indiquent une tendance, pas une statistique nationale.
- La source actuelle ne contient que des offres en alternance, pas de CDI ni de CDD.
- L'API est limitee a 150 resultats par requete et par source.
- Les competences sont detectees par dictionnaire (79 technologies) : 14 offres sur 43 n'ont aucune technologie detectee, et certains termes peuvent etre ambigus (par exemple "reseau").
