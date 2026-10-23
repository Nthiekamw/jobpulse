import os
import requests
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
API_URL = (
    "https://api.francetravail.io/partenaire/"
    "stats-offres-demandes-emploi/v1/indicateur/stat-demandeurs"
)

def main():
    client_id = os.getenv("FT_CLIENT_ID")
    client_secret = os.getenv("FT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Erreur : identifiants absents du fichier .env")
        return

    auth = requests.post(
        AUTH_URL,
        params={"realm": "/partenaire"},
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "api_stats-offres-demandes-emploiv1 offresetdemandesemploi",
        },
        timeout=30,
    )

    print("Authentification :", auth.status_code)
    if not auth.ok:
        print(auth.text[:1000])
        return

    token = auth.json()["access_token"]

    payload = {
        "codeTypeTerritoire": "DEP",
        "codeTerritoire": "93",
        "codeTypeActivite": "ROME",
        "codeActivite": "M1805",
        "codeTypePeriode": "TRIMESTRE",
        "codeTypeNomenclature": "CATCAND",
        "dernierePeriode": True,
        "sansCaracteristiques": True,
    }

    response = requests.post(
        API_URL,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=60,
    )

    print("Réponse API :", response.status_code)
    try:
        print(response.text[:3000])
    except Exception:
        print("Réponse reçue, mais impossible de l'afficher.")

if __name__ == "__main__":
    main()
