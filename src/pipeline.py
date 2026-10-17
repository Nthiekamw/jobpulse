import importlib
from datetime import datetime
from config import SOURCES

dossier = "data/bronze/" + datetime.now().strftime("%Y-%m-%d")
for nom, cfg in SOURCES.items():
    if not cfg.get("actif"):
        print(nom, ": desactivee")
        continue
    module = importlib.import_module("sources." + nom)
    print(nom, ":", module.collecter(cfg, dossier), "offres collectees")
