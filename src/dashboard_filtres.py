import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="JobPulse", page_icon="📊", layout="wide")
COULEUR = "#1F6FEB"

@st.cache_data
def charger():
    return pd.read_parquet("data/silver/export_offres_competences")

def barres(df, x, y, hauteur=420):
    fig = px.bar(df.sort_values(x), x=x, y=y, orientation="h", text=x)
    fig.update_traces(marker_color=COULEUR, textposition="outside", cliponaxis=False)
    fig.update_yaxes(type="category", title=None)
    fig.update_xaxes(title=None, showgrid=False, visible=False)
    fig.update_layout(height=hauteur, margin=dict(l=0, r=30, t=10, b=0))
    return fig

d = charger()
d["type_contrat_normalise"] = d["type_contrat_normalise"].fillna("Non renseigné")

st.sidebar.header("Filtres")
sources = sorted(d["source"].dropna().unique())
choix_sources = st.sidebar.multiselect("Source", sources)
contrats = sorted(d["type_contrat_normalise"].unique())
choix_contrats = st.sidebar.multiselect("Type de contrat", contrats)

if choix_sources:
    d = d[d["source"].isin(choix_sources)]
if choix_contrats:
    d = d[d["type_contrat_normalise"].isin(choix_contrats)]

st.title("📊 JobPulse")
st.markdown("**Plateforme d'analyse des offres d'emploi** · Pipeline Big Data Spark · Architecture Bronze / Silver / Gold")

avec_tech = int(d["competences_extraites"].apply(len).gt(0).sum())
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Offres analysées", f"{len(d):,}".replace(",", " "))
c2.metric("CDI identifiés", int((d["type_contrat_normalise"] == "CDI").sum()))
c3.metric("CDD identifiés", int((d["type_contrat_normalise"] == "CDD").sum()))
c4.metric("Intérim", int((d["type_contrat_normalise"] == "Intérim").sum()))
c5.metric("Alternances", int((d["type_contrat_normalise"] == "Alternance").sum()))
c6.metric("Technologies détectées", avec_tech)

st.divider()
st.subheader("Répartition des contrats")
contrat_counts = d["type_contrat_normalise"].value_counts().rename_axis("contrat").reset_index(name="nb_offres")
st.plotly_chart(barres(contrat_counts, "nb_offres", "contrat"), width="stretch")
st.caption("Les contrats temporaires Adzuna ne sont pas automatiquement assimilés à des CDD.")

st.divider()
st.subheader("Évolution des offres publiées")
dates = pd.to_datetime(d["date_publication"], errors="coerce")
mensuel = dates.dt.to_period("M").value_counts().sort_index()
if not mensuel.empty:
    evolution = mensuel.rename_axis("mois").reset_index(name="nb_offres")
    evolution["mois"] = evolution["mois"].astype(str)
    fig = px.line(evolution, x="mois", y="nb_offres", markers=True)
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Aucune date de publication disponible.")
st.caption("Distribution des dates présentes dans les données collectées, et non mesure exhaustive du marché.")

st.divider()
st.subheader("Secteurs d'activité")
secteurs = d["secteur_naf"].dropna()
secteurs = secteurs[secteurs.str.strip() != ""].value_counts().head(15)
if not secteurs.empty:
    st.plotly_chart(barres(secteurs.rename_axis("secteur").reset_index(name="nb_offres"),
                           "nb_offres", "secteur", 550), width="stretch")
else:
    st.info("Aucune donnée sectorielle disponible pour cette sélection.")

st.divider()
st.subheader("Salaires des offres Adzuna")
salaires = d[(d["source"] == "adzuna") & (d["salaire_min"].notna() | d["salaire_max"].notna())]
if not salaires.empty:
    st.dataframe(
        salaires[["titre", "entreprise", "salaire_min", "salaire_max", "salaire_estime", "type_contrat_normalise"]],
        width="stretch"
    )
else:
    st.info("Aucune donnée salariale disponible.")
st.caption("Montants bruts transmis par la source. Leur périodicité et leur unité ne sont pas confirmées : aucune moyenne n'est calculée.")

st.divider()
st.subheader("Technologies les plus demandées")
n = st.slider("Nombre de technologies", 5, 30, 12)
top = d["competences_extraites"].explode().dropna().value_counts().head(n)
top = top.rename_axis("technologie").reset_index(name="nb_offres")
top["technologie"] = top["technologie"].str.title()
if not top.empty:
    st.plotly_chart(barres(top, "nb_offres", "technologie", 60 + 32 * n), width="stretch")
st.caption("Technologies détectées automatiquement dans les titres et descriptions.")

st.divider()
g, s = st.columns(2)
dept = d.loc[d["departement"].notna() & (d["departement"] != ""), "departement"].value_counts().head(10)
g.subheader("Offres par département")
if not dept.empty:
    g.plotly_chart(barres(dept.rename_axis("departement").reset_index(name="nb_offres"),
                          "nb_offres", "departement"), width="stretch")
src = d["source"].value_counts()
s.subheader("Offres par source")
s.plotly_chart(barres(src.rename_axis("source").reset_index(name="nb_offres"),
                      "nb_offres", "source"), width="stretch")

st.divider()
st.subheader("Métiers les plus présents (code ROME)")
t = d[["titre", "codes_rome"]].explode("codes_rome").dropna()
if not t.empty:
    m = t.groupby("codes_rome").agg(
        nb_offres=("titre", "size"),
        intitule_frequent=("titre", lambda x: x.value_counts().index[0])
    )
    st.dataframe(m.sort_values("nb_offres", ascending=False).head(15), width="stretch")
