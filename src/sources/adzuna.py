import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.adzuna.com/v1/api/jobs/fr/search/{}"


def collecter(config, dossier):
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise ValueError("Identifiants Adzuna absents du fichier .env")

    os.makedirs(dossier, exist_ok=True)

    page = 1
    total = 0
    max_pages = config.get("max_pages", 1)

    while page <= max_pages:
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 50,
            "category": "it-jobs",
            "content-type": "application/json",
        }

        response = requests.get(
            URL.format(page),
            params=params,
            timeout=30
        )

        if response.status_code == 429:
            raise RuntimeError("Quota Adzuna atteint (429)")

        response.raise_for_status()

        donnees = response.json()
        offres = donnees.get("results", [])

        if not offres:
            break

        chemin = os.path.join(dossier, f"adzuna_page_{page}.json")

        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)

        total += len(offres)

        print(f"Adzuna page {page} : {len(offres)} offres -> {chemin}")

        if len(offres) < 50:
            break

        page += 1

    return total
