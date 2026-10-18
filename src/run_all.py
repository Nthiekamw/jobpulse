import csv
import os
import shutil
import subprocess
import sys
import time

ETAPES = [
    ("Telechargement de l'export", "src/telecharger_export.py"),
    ("Conversion en JSON Lines", "src/convertir_export.py"),
    ("Silver : offres et recruteurs", "src/silver_export.py"),
    ("Extraction des competences", "src/silver_competences_export.py"),
    ("Gold : tables d'agregation", "src/gold_export.py"),
]
sans_telechargement = "--sans-telechargement" in sys.argv
os.makedirs("data/logs", exist_ok=True)
resultats = []

for nom, script in ETAPES:
    if sans_telechargement and script.endswith("telecharger_export.py"):
        continue
    if script.endswith("convertir_export.py"):
        shutil.rmtree("data/bronze/export_jsonl", ignore_errors=True)
    debut = time.time()
    with open("data/logs/" + os.path.basename(script) + ".log", "w") as log:
        code = subprocess.run([sys.executable, script], stdout=log, stderr=subprocess.STDOUT).returncode
    duree = round(time.time() - debut)
    statut = "OK" if code == 0 else "ERREUR"
    resultats.append((nom, duree, statut))
    print(statut, "-", nom, ":", duree, "s", flush=True)
    if code != 0:
        print("Arret : voir data/logs/" + os.path.basename(script) + ".log")
        break

with open("performances.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["etape", "duree_secondes", "statut"])
    w.writerows(resultats)
print("Total :", sum(r[1] for r in resultats), "s | detail dans performances.csv")
