import re
import unicodedata
from technologies import TECHNOLOGIES


def normaliser(texte):
    texte = unicodedata.normalize("NFD", texte or "")
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return texte.lower()


MOTIFS = {t: re.compile(r"(?<![a-z0-9])" + re.escape(t) + r"(?![a-z0-9])") for t in TECHNOLOGIES}


def extraire(titre, description):
    texte = normaliser((titre or "") + " " + (description or ""))
    return sorted(t for t, m in MOTIFS.items() if m.search(texte))
