import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
URL = "https://api.apprentissage.beta.gouv.fr/api/job/v1/search"


def collecter(config, dossier):
    cle = os.getenv("LBA_API_KEY")
    os.makedirs(dossier, exist_ok=True)
    total = 0
    for rome in config["codes_rome"]:
        r = requests.get(URL, headers={"Authorization": "Bearer " + cle},
                         params={"romes": rome}, timeout=30)
        if r.ok:
            donnees = r.json()
            with open(dossier + "/offres_" + rome + ".json", "w", encoding="utf-8") as f:
                json.dump(donnees, f, ensure_ascii=False)
            total += len(donnees.get("jobs", []))
        else:
            print("  erreur", r.status_code, "pour", rome)
        time.sleep(1.5)
    return total
