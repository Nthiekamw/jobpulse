import os
import requests
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv("FT_CLIENT_ID")
client_secret = os.getenv("FT_CLIENT_SECRET")

url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
reponse = requests.post(
    url,
    params={"realm": "/partenaire"},
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "api_rome-competencesv1",
    },
    timeout=30,
)

print("Statut HTTP :", reponse.status_code)
if reponse.ok:
    print("Jeton recu, expire dans (secondes) :", reponse.json().get("expires_in"))
else:
    print("Erreur :", reponse.text[:300])
