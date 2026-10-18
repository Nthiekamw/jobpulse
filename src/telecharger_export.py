import os
import requests
from dotenv import load_dotenv

load_dotenv()
r = requests.get("https://api.apprentissage.beta.gouv.fr/api/job/v1/export",
                 headers={"Authorization": "Bearer " + os.getenv("LBA_API_KEY")}, timeout=30)
r.raise_for_status()
d = r.json()
os.makedirs("data/bronze/export", exist_ok=True)
chemin = "data/bronze/export/export_courant.bin"
n = 0
with requests.get(d["url"], stream=True, timeout=120) as f, open(chemin, "wb") as out:
    for morceau in f.iter_content(chunk_size=1024 * 1024):
        out.write(morceau)
        n += len(morceau)
print("Export du", d["lastUpdate"], ":", round(n / 1e6, 1), "Mo")
