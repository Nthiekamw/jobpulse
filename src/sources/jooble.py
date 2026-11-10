import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env")

URL = "https://fr.jooble.org/api/"

def collecter(config, dossier):
    key = os.getenv("JOOBLE_API_KEY")
    if not key:
        raise ValueError("JOOBLE_API_KEY absente")

    os.makedirs(dossier, exist_ok=True)
    brut = os.path.join(dossier, "jooble_recherches")
    os.makedirs(brut, exist_ok=True)

    recherches = ["CDI", "CDD"]
    toutes = {}
    total_requetes = 0

    for recherche in recherches:
        print(f"\nRecherche {recherche}")

        for page in range(1, 11):
            payload = {
                "keywords": recherche,
                "location": "France",
                "page": page,
                "ResultOnPage": 50,
                "companysearch": False
            }

            r = requests.post(URL + key, json=payload, timeout=30)
            if not r.ok:
                raise RuntimeError(
                    f"Jooble HTTP {r.status_code} - {r.text[:300]}"
                )

            data = r.json()
            total_requetes += 1
            offres = data.get("jobs", [])

            fichier = os.path.join(
                brut, f"{recherche.lower()}_page_{page}.json"
            )
            with open(fichier, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            for offre in offres:
                identifiant = offre.get("id") or offre.get("link")
                if identifiant:
                    toutes[str(identifiant)] = offre

            print(
                f"Page {page}: {len(offres)} offres "
                f"| Total annoncé: {data.get('totalCount', 0)}"
            )

            if not offres:
                break

    resultat = {
        "totalCount": len(toutes),
        "jobs": list(toutes.values())
    }

    with open(
        os.path.join(dossier, "jooble_page_1.json"),
        "w", encoding="utf-8"
    ) as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)

    print("\n===== BILAN =====")
    print("Requêtes utilisées :", total_requetes)
    print("Offres uniques récupérées :", len(toutes))
    print("Fichier agrégé : jooble_page_1.json")

    return len(toutes)
