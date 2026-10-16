import os
import json
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
API_URL = (
    "https://api.francetravail.io/partenaire/"
    "stats-offres-demandes-emploi/v1/indicateur/stat-demandeurs"
)

CODES_ROME = ["M1801", "M1802", "M1803", "M1805", "M1806", "M1810"]


def obtenir_jeton():
    reponse = requests.post(
        AUTH_URL,
        params={"realm": "/partenaire"},
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("FT_CLIENT_ID"),
            "client_secret": os.getenv("FT_CLIENT_SECRET"),
            "scope": "api_stats-offres-demandes-emploiv1 offresetdemandesemploi",
        },
        timeout=30,
    )
    reponse.raise_for_status()
    return reponse.json()["access_token"]


def collecter():
    jeton = obtenir_jeton()
    resultats = []

    for code in CODES_ROME:
        payload = {
            "codeTypeTerritoire": "DEP",
            "codeTerritoire": "93",
            "codeTypeActivite": "ROME",
            "codeActivite": code,
            "codeTypePeriode": "TRIMESTRE",
            "codeTypeNomenclature": "CATCAND",
            "dernierePeriode": True,
            "sansCaracteristiques": True,
        }

        reponse = requests.post(
            API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {jeton}",
                "Accept": "application/json",
            },
            timeout=60,
        )

        if reponse.ok:
            resultats.append(reponse.json())
            print(f"{code} : OK")
        else:
            print(f"{code} : erreur {reponse.status_code}")
            print(reponse.text[:300])

    date_jour = datetime.now().strftime("%Y-%m-%d")
    dossier = f"data/bronze/{date_jour}"
    os.makedirs(dossier, exist_ok=True)

    chemin = f"{dossier}/marche_travail_93.json"
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(resultats, fichier, ensure_ascii=False, indent=2)

    print(f"Résultats enregistrés : {chemin}")
    print(f"Réponses collectées : {len(resultats)}/{len(CODES_ROME)}")


if __name__ == "__main__":
    collecter()
