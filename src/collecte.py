import os
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()
CLE = os.getenv("LBA_API_KEY")
URL = "https://api.apprentissage.beta.gouv.fr/api/job/v1/search"

# Codes ROME des métiers informatiques à collecter
CODES_ROME = ["M1801", "M1802", "M1803", "M1805", "M1806", "M1810"]

date_jour = datetime.now().strftime("%Y-%m-%d")
dossier = f"data/bronze/{date_jour}"
os.makedirs(dossier, exist_ok=True)

for rome in CODES_ROME:
    reponse = requests.get(
        URL,
        headers={"Authorization": f"Bearer {CLE}"},
        params={"romes": rome},
        timeout=30,
    )
    if reponse.ok:
        donnees = reponse.json()
        chemin = f"{dossier}/offres_{rome}.json"
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False)
        print(f"{rome} : {len(donnees.get('jobs', []))} offres -> {chemin}")
    else:
        print(f"{rome} : ERREUR {reponse.status_code}")
    time.sleep(1.5)  # on respecte la limite de 60 appels par minute
