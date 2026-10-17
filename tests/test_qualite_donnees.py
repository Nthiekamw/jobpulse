import os
import pandas as pd
import pytest
from technologies import TECHNOLOGIES

SILVER = "data/silver/offres_competences"
GOLD = "data/gold/"

pytestmark = pytest.mark.skipif(not os.path.isdir(SILVER), reason="donnees absentes")


def silver():
    return pd.read_parquet(SILVER)


def test_silver_pas_de_doublons():
    assert silver()["id_offre"].is_unique


def test_silver_id_renseigne():
    ids = silver()["id_offre"]
    assert ids.notna().all() and (ids != "").all()


def test_silver_titre_renseigne():
    titres = silver()["titre"]
    assert titres.notna().all() and (titres.str.len() >= 3).all()


def test_gold_total_source_egal_silver():
    par_source = pd.read_parquet(GOLD + "offres_par_source")
    assert int(par_source["nb_offres"].sum()) == len(silver())


def test_gold_pourcentages_valides():
    top = pd.read_parquet(GOLD + "top_technologies")
    assert ((top["pct_offres"] >= 0) & (top["pct_offres"] <= 100)).all()


def test_competences_connues_du_dictionnaire():
    trouvees = {t for liste in silver()["competences_extraites"] for t in liste}
    assert trouvees <= set(TECHNOLOGIES)
