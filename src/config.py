# Une entree par source. Pour ajouter une source : creer src/sources/<nom>.py
# avec une fonction collecter(config, dossier), puis ajouter une ligne ici.
SOURCES = {
    "lba": {
        "actif": True,
        "codes_rome": ["M1801", "M1802", "M1803", "M1805", "M1806", "M1810"],
    },
    "adzuna": {"actif": True, "max_pages": 1},
    "jooble": {"actif": True, "keywords": "développeur informatique", "location": "France"},
}
