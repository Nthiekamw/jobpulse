# JobPulse

Plateforme de collecte et d'analyse d'offres d'emploi en alternance, construite avec Python et Apache Spark (projet de fin d'etudes : conception d'une plateforme Big Data de collecte et d'analyse des offres d'emploi).

## Presentation

JobPulse telecharge chaque jour l'export complet des offres d'emploi en alternance publiees par La bonne alternance (environ 600 Mo), les nettoie avec Spark, detecte les logiciels et outils demandes dans les descriptions, puis agrege les resultats dans des tables pretes pour un tableau de bord. L'architecture est modulaire : une nouvelle source de donnees s'ajoute sans modifier le reste du pipeline.

Volume traite lors du dernier export (17/10/2026) : 306 263 enregistrements, dont 12 957 offres distinctes et 293 306 entreprises susceptibles de recruter.

## Architecture

| Couche | Contenu | Emplacement |
|---|---|---|
| Bronze | Donnees brutes : export JSON converti en JSON Lines, reponses d'API | data/bronze/ |
| Silver | Offres et recruteurs dedoublonnes, competences extraites (Parquet) | data/silver/ |
| Gold | Tables d'agregation pour le tableau de bord (Parquet) | data/gold_export/ |

Flux : API, telechargement, conversion en flux (ijson), Spark (Silver), extraction des competences, Spark (Gold), tableau de bord Streamlit.

## Sources de donnees

- **La bonne alternance** : API de recherche (src/sources/lba.py, pipeline modulaire) et route d'export complet (src/telecharger_export.py). Usage non lucratif uniquement.
- **France Travail** : scripts de collecte du referentiel ROME 4.0 et des statistiques du marche du travail (src/competences_rome.py, src/marche_travail.py). Ils ne sont pas integres au pipeline principal.

## Installation

Prerequis : Python 3.12 et Java 21 (necessaire a Spark).

    uv venv --python 3.12 .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt

Creer un fichier .env a la racine (ignore par Git) :

    LBA_API_KEY=votre_cle

## Utilisation

Pipeline complet en une commande (mesure la duree de chaque etape) :

    python src/run_all.py

Relancer sans retelecharger l'export :

    python src/run_all.py --sans-telechargement

Tableau de bord (optionnel, il ne fait que lire les tables Gold) :

    streamlit run src/dashboard_filtres.py

Les tables Gold sont des fichiers Parquet lisibles directement avec pandas.

## Tests

    python -m pytest tests/ -v

12 tests : extraction des competences (dont un test contre les faux positifs) et qualite des donnees (pas de doublons, identifiants renseignes, coherence des totaux entre Silver et Gold).

## Performances

Mesures sur un Codespace de 2 coeurs et 7,8 Go de memoire, Spark en mode local (fichier performances.csv) :

| Etape | Duree |
|---|---|
| Telechargement de l'export (606 Mo) | 22 s |
| Conversion en JSON Lines | 23 s |
| Silver : offres et recruteurs | 41 s |
| Extraction des competences | 143 s |
| Gold : tables d'agregation | 21 s |
| Total | 250 s |

L'extraction des competences est le goulot d'etranglement : elle applique une fonction Python a chaque description.

## Ajouter une source

1. Creer src/sources/nom_de_la_source.py avec une fonction collecter(config, dossier) qui ecrit ses fichiers JSON dans le dossier donne et renvoie le nombre d'offres collectees.
2. Declarer la source dans src/config.py (cle "actif" a True).

## Limites connues

- Les offres sont uniquement des offres en alternance : pas de CDI ni de CDD.
- 96 % de l'export sont des entreprises sans offre deposee, pas des offres.
- Les competences sont detectees par dictionnaire (99 logiciels et technologies) : seules environ 5 % des offres ont au moins une detection, car la plupart des offres decrivent des competences metier et non des outils.
- Des faux positifs ont ete corriges (par exemple "vue", "reseau", "tableau") ; d'autres termes peuvent rester ambigus.
- Spark tourne en mode local sur une seule machine : les temps ne sont pas representatifs d'un cluster.
- Pas de traitement en temps reel (streaming) pour le moment.
