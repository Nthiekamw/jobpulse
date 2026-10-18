import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="JobPulse", page_icon="📊", layout="wide")
COULEUR = "#1F6FEB"


@st.cache_data
def charger():
    cols = ["id_offre", "source", "titre", "codes_rome", "departement", "competences_extraites"]
    return pd.read_parquet("data/silver/export_offres_competences", columns=cols)


def barres(df, x, y, hauteur=420):
    fig = px.bar(df.sort_values(x), x=x, y=y, orientation="h", text=x)
    fig.update_traces(marker_color=COULEUR, textposition="outside", cliponaxis=False)
    fig.update_yaxes(type="category", title=None)
    fig.update_xaxes(title=None, showgrid=False, visible=False)
    fig.update_layout(height=hauteur, margin=dict(l=0, r=30, t=10, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


d = charger()
st.sidebar.header("Filtres")
sources = sorted(d["source"].dropna().unique())
choix = st.sidebar.multiselect("Source (vide = toutes)", sources)
if choix:
    d = d[d["source"].isin(choix)]

st.title("📊 JobPulse")
st.markdown("**Offres d'emploi en alternance** · Source : La bonne alternance · Pipeline Spark Bronze / Silver / Gold")
avec_tech = int(d["competences_extraites"].apply(len).gt(0).sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Offres analysees", f"{len(d):,}".replace(",", " "))
c2.metric("Avec une technologie detectee", f"{avec_tech:,}".replace(",", " "))
c3.metric("Departements", d.loc[d["departement"] != "", "departement"].nunique())
c4.metric("Sources", d["source"].nunique())

st.divider()
st.subheader("Technologies les plus demandees")
n = st.slider("Nombre de technologies", 5, 30, 12)
top = d["competences_extraites"].explode().dropna().value_counts().head(n)
top = top.rename_axis("technologie").reset_index(name="nb_offres")
top["technologie"] = top["technologie"].str.title()
if len(top):
    st.plotly_chart(barres(top, "nb_offres", "technologie", 60 + 32 * n), width="stretch")
st.caption("Nombre d'offres dont la description mentionne l'outil. Dictionnaire limite aux logiciels courants.")

st.divider()
g, s = st.columns(2)
dept = d.loc[d["departement"] != "", "departement"].value_counts().head(10)
g.subheader("Offres par departement")
g.plotly_chart(barres(dept.rename_axis("departement").reset_index(name="nb_offres"), "nb_offres", "departement"), width="stretch")
g.caption("Les codes 97x correspondent a l'outre-mer.")
src = d["source"].value_counts().head(12)
s.subheader("Offres par source")
s.plotly_chart(barres(src.rename_axis("source").reset_index(name="nb_offres"), "nb_offres", "source"), width="stretch")
s.caption("Plateforme qui diffuse l'offre.")

st.divider()
st.subheader("Metiers les plus presents (code ROME)")
t = d[["titre", "codes_rome"]].explode("codes_rome").dropna()
m = t.groupby("codes_rome").agg(nb_offres=("titre", "size"),
                                 intitule_frequent=("titre", lambda x: x.value_counts().index[0]))
st.dataframe(m.sort_values("nb_offres", ascending=False).head(15), width="stretch")
st.caption("Intitule le plus frequent parmi les offres de chaque code : etiquette deduite des donnees, pas le nom officiel ROME.")
