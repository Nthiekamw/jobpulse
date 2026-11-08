import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env")

URL = "https://jooble.org/api/"

def collecter(config, dossier):
    key = os.getenv("JOOBLE_API_KEY")
    if not key:
        raise ValueError("JOOBLE_API_KEY absente du fichier .env")

    os.makedirs(dossier, exist_ok=True)
    payload = {
        "keywords": config.get("keywords", "développeur informatique"),
        "location": config.get("location", "France"),
        "page": 1
    }

    response = requests.post(URL + key, json=payload, timeout=30)
    response.raise_for_status()
    donnees = response.json()

    chemin = os.path.join(dossier, "jooble_page_1.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

    total = len(donnees.get("jobs", []))
    print(f"Jooble : {total} offres -> {chemin}")
    return total
