import os
import requests
from dotenv import load_dotenv

load_dotenv()
cle = os.getenv("LBA_API_KEY")

url = "https://api.apprentissage.beta.gouv.fr/api/job/v1/search"
reponse = requests.get(
    url,
    headers={"Authorization": f"Bearer {cle}"},
    params={"romes": "M1805"},
    timeout=30,
)

print("Statut HTTP :", reponse.status_code)
if reponse.ok:
    donnees = reponse.json()
    offres = donnees.get("jobs", [])
    print("Nombre d'offres recues :", len(offres))
    if offres:
        print("Premier titre :", offres[0]["offer"]["title"])
else:
    print("Erreur :", reponse.text[:300])
