import json
import re
from pathlib import Path
from html import unescape

FICHIER = Path("data/bronze/2026-11-09/jooble_page_1.json")

def nettoyer(texte):
    texte = unescape(str(texte or ""))
    texte = re.sub(r"<[^>]+>", " ", texte)
    return re.sub(r"\s+", " ", texte).strip()

def classifier(offre):
    titre = nettoyer(offre.get("title", "")).upper()
    description = nettoyer(offre.get("snippet", "")).upper()

    # Le titre constitue l'indication la plus directe.
    if re.search(r"\bCDI\b", titre):
        return "CDI"
    if re.search(r"\bCDD\b", titre):
        return "CDD"

    # Expressions qui indiquent explicitement le contrat du poste.
    motifs = [
        (r"\bTYPE\s+(?:DE\s+)?(?:CONTRAT|EMPLOI)\s*[:\-]?\s*CDD\b", "CDD"),
        (r"\bTYPE\s+(?:DE\s+)?(?:CONTRAT|EMPLOI)\s*[:\-]?\s*CDI\b", "CDI"),
        (r"\bPOSTE\s+(?:EST\s+)?EN\s+CDD\b", "CDD"),
        (r"\bPOSTE\s+(?:EST\s+)?EN\s+CDI\b", "CDI"),
        (r"\bCONTRAT\s+(?:À|A)\s+DURÉE\s+DÉTERMINÉE\b", "CDD"),
        (r"\bCONTRAT\s+(?:À|A)\s+DURÉE\s+INDÉTERMINÉE\b", "CDI"),
        (r"\bCDD\s+(?:DE|D['’])\s*\d+\s*(?:MOIS|AN|ANS)\b", "CDD"),
        (r"\bCDI\s+(?:À|A)\s*TEMPS\b", "CDI"),
        (r"\bRECRUTEMENT\s+EN\s+CDD\b", "CDD"),
        (r"\bRECRUTEMENT\s+EN\s+CDI\b", "CDI"),
        (r"\bEMBAUCHE\s+EN\s+CDD\b", "CDD"),
        (r"\bEMBAUCHE\s+EN\s+CDI\b", "CDI"),
    ]

    # Retirer les formulations génériques des agences d'intérim.
    generiques = [
        r"NOUS PROPOSONS DES CONTRATS?.{0,100}?(?:CDD|CDI)",
        r"RECRUTEMENT.{0,100}?(?:CDD|CDI).{0,80}?INTÉRIM",
        r"EN INTÉRIM.{0,100}?(?:CDD|CDI)",
        r"(?:CDD|CDI).{0,80}?OU EN INTÉRIM",
        r"MISSIONS EN (?:CDI|CDD|CDII|INTÉRIM)",
        r"EN (?:CDI|CDD) ET INTÉRIM",
    ]
    texte = description
    for motif in generiques:
        texte = re.sub(motif, " ", texte)

    resultats = {
        contrat
        for motif, contrat in motifs
        if re.search(motif, texte)
    }

    return resultats.pop() if len(resultats) == 1 else None

with FICHIER.open(encoding="utf-8") as f:
    data = json.load(f)

compteurs = {"CDI": 0, "CDD": 0, "Non déterminé": 0}

for offre in data["jobs"]:
    offre["type_original"] = offre.get("type", "")
    contrat = classifier(offre)
    offre["type_contrat"] = contrat
    if contrat:
        offre["type"] = contrat
        compteurs[contrat] += 1
    else:
        compteurs["Non déterminé"] += 1

data["totalCount"] = len(data["jobs"])

with FICHIER.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Classification terminée :", len(data["jobs"]), "offres")
for contrat, nombre in compteurs.items():
    print(f"{contrat} : {nombre}")
print("Champ d'origine conservé dans type_original.")
