import ijson
import json
import os
from collections import Counter

SRC = "data/bronze/export/export_courant.bin"
DEST = "data/bronze/export_jsonl"
TAILLE = 20000

os.makedirs(DEST, exist_ok=True)
compte = Counter()
n = 0
part = 0
sortie = None

with open(SRC, "rb") as f:
    for obj in ijson.items(f, "item", use_float=True):
        if n % TAILLE == 0:
            if sortie:
                sortie.close()
            sortie = open(DEST + "/export_%03d.jsonl" % part, "w", encoding="utf-8")
            part += 1
        sortie.write(json.dumps(obj, ensure_ascii=False) + "\n")
        compte[obj.get("identifier", {}).get("partner_label")] += 1
        n += 1
if sortie:
    sortie.close()

print("Objets convertis :", n, "| fichiers :", part)
for label, nb in compte.most_common(12):
    print(" ", label, ":", nb)
