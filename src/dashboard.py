import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="JobPulse", page_icon="📊", layout="wide")
COULEUR = "#1F6FEB"
NOMS_ROME = {
    "M1801": "Administration de systemes d'information",
    "M1802": "Expertise et support en SI",
    "M1803": "Direction des systemes d'information",
    "M1805": "Etudes et developpement informatique",
    "M1806": "Conseil et maitrise d'ouvrage en SI",
    "M1810": "Production et exploitation de SI",
}


def charger(nom):
    return pd.read_parquet("data/gold/" + nom)


def barres(df, x, y, hauteur=420):
    fig = px.bar(df.sort_values(x), x=x, y=y, orientation="h", text=x)
    fig.update_traces(marker_color=COULEUR, textposition="outside", cliponaxis=False)
    fig.update_yaxes(type="category", title=None)
    fig.update_xaxes(title=None, showgrid=False, visible=False)
    fig.update_layout(height=hauteur, margin=dict(l=0, r=30, t=10, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


top = charger("top_technologies")
dept = charger("offres_par_departement")
source = charger("offres_par_source")
rome = charger("offres_par_rome")

st.title("📊 JobPulse")
st.markdown("**Offres d'emploi en alternance dans l'informatique** · Source : La bonne alternance · Pipeline Spark Bronze / Silver / Gold")

total = int(source["nb_offres"].sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Offres analysees", total)
c2.metric("Technologies detectees", len(top))
c3.metric("Departements", len(dept))
c4.metric("Sources", len(source))

st.divider()
st.subheader("Technologies les plus demandees")
n = st.slider("Nombre de technologies", 5, 30, 12)
t = top.head(n).copy()
t["technologie"] = t["technologie"].str.title()
st.plotly_chart(barres(t, "nb_offres", "technologie", 60 + 32 * n), use_container_width=True)

st.divider()
g, d = st.columns(2)
g.subheader("Offres par departement")
g.plotly_chart(barres(dept.head(10), "nb_offres", "departement"), use_container_width=True)
d.subheader("Offres par source")
d.plotly_chart(barres(source, "nb_offres", "source"), use_container_width=True)

st.divider()
st.subheader("Offres par metier (code ROME)")
rome["metier"] = rome["code_rome"].map(NOMS_ROME).fillna(rome["code_rome"])
st.dataframe(rome[["code_rome", "metier", "nb_offres"]], hide_index=True, use_container_width=True)
st.caption("Echantillon de 41 offres : les resultats indiquent une tendance, pas une statistique nationale.")
