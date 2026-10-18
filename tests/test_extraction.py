from extraction import extraire, normaliser


def test_detecte_technologies():
    assert extraire("Dev", "Python et SQL") == ["python", "sql"]


def test_ignore_accents_et_majuscules():
    assert "reseaux informatiques" in extraire("Technicien", "Réseaux Informatiques")


def test_java_ne_matche_pas_javascript():
    r = extraire("", "JavaScript uniquement")
    assert "javascript" in r and "java" not in r


def test_texte_vide():
    assert extraire(None, None) == []


def test_normaliser():
    assert normaliser("Cybersécurité") == "cybersecurite"


def test_pas_de_faux_positifs():
    assert extraire("", "en vue de, point de vue, reseau de distribution, tableau de bord") == []
