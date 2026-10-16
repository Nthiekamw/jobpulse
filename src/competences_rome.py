import os
import json
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("FT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FT_CLIENT_SECRET")

URL_AUTH = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
URL_API = "https://api.francetravail.io/partenaire/rome-competences/v1/competences/competence"


def obtenir_jeton():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("FT_CLIENT_ID ou FT_CLIENT_SECRET absent du fichier .env")

    reponse = requests.post(
        URL_AUTH,
        params={"realm": "/partenaire"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "api_rome-competencesv1 nomenclatureRome",
        },
        timeout=30,
    )
    reponse.raise_for_status()
    return reponse.json()["access_token"]


def collecter_competences():
    jeton = obtenir_jeton()

    reponse = requests.get(
        URL_API,
        params={"champs": "code,libelle"},
        headers={
            "Authorization": f"Bearer {jeton}",
            "Accept": "application/json",
        },
        timeout=60,
    )
    reponse.raise_for_status()

    competences = reponse.json()

    date_jour = datetime.now().strftime("%Y-%m-%d")
    dossier = f"data/bronze/{date_jour}"
    os.makedirs(dossier, exist_ok=True)

    chemin = f"{dossier}/competences_rome.json"

    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(competences, fichier, ensure_ascii=False, indent=2)

    print("Nombre de compétences :", len(competences))
    print("Fichier enregistré :", chemin)

    if competences:
        print("Exemple :", competences[0])


if __name__ == "__main__":
    collecter_competences()
