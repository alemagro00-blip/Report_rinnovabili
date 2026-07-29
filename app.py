import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# CONFIGURAZIONE PAGINA
# =========================================================
st.set_page_config(
    page_title="La Corsa alle Rinnovabili",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# FUNZIONI HELPER
# ==============================================================================

def forza_sfondo_bianco(fig):
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        # Forziamo il colore del font a livello globale del grafico
        font=dict(color="#1e293b", family="Inter, sans-serif"),
        title=dict(font=dict(color="#1B4332")),
        legend=dict(font=dict(color="#1e293b"))
    )
    
    # Sovrascriviamo gli assi X e Y per evitare che Plotly li sbianchi
    fig.update_xaxes(
        tickfont=dict(color="#1e293b"),
        title=dict(font=dict(color="#1e293b")),
        color="#1e293b",
        gridcolor="#e2e8f0"
    )
    fig.update_yaxes(
        tickfont=dict(color="#1e293b"),
        title=dict(font=dict(color="#1e293b")),
        color="#1e293b",
        gridcolor="#e2e8f0"
    )
    return fig
# =========================================================
# RILEVAMENTO DISPOSITIVO (Mobile vs Desktop)
# =========================================================
def is_mobile():
    """Rileva se l'utente è su un dispositivo mobile controllando lo User-Agent dagli header HTTP di Streamlit."""
    try:
        user_agent = st.context.headers.get("User-Agent", "").lower()
        mobile_keywords = ["mobile", "android", "iphone", "ipad", "ipod", "blackberry", "windows phone"]
        return any(keyword in user_agent for keyword in mobile_keywords)
    except Exception:
        return False

IS_MOBILE = is_mobile()

# =========================================================
# STILE GRAFICO (tema verde, font moderni, fix layout mobile)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sfondo dell'app chiaro */
.stApp {
    background-color: #ffffff !important;
    color: #1e293b !important;
}

.main .block-container {
    max-width: 1080px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #1B4332 !important;
}

/* Hero */
.hero-title {
    font-size: 2.9rem;
    font-weight: 700;
    line-height: 1.15;
    background: linear-gradient(90deg, #1B4332, #2D6A4F, #52B788);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
    font-family: 'Space Grotesk', sans-serif;
}
.hero-subtitle {
    font-size: 1.12rem;
    color: #52796F;
    max-width: 720px;
    margin-bottom: 2.2rem;
    line-height: 1.5;
}

/* Indice */
.toc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 12px;
    margin-bottom: 3rem;
}
.toc-card {
    background: #F1F8F4;
    border: 1px solid #D8F3DC;
    border-radius: 14px;
    padding: 16px 18px;
    text-decoration: none !important;
    color: #1B4332 !important;
    font-weight: 600;
    font-size: 0.98rem;
    transition: all 0.2s ease;
    display: block;
}
.toc-card:hover {
    background: #D8F3DC;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(27,67,50,0.15);
}

/* Testo introduttivo di sezione */
.section-intro {
    font-size: 1.06rem;
    line-height: 1.75;
    color: #33413A;
    margin-bottom: 0.6rem;
}

/* Box di approfondimento / insight */
.insight-box {
    background: #F7FBF8;
    border-left: 4px solid #52B788;
    border-radius: 10px;
    padding: 18px 22px;
    margin: 1.3rem 0 2.6rem 0;
    font-size: 1.02rem;
    line-height: 1.7;
    color: #2D3A34;
}
.insight-box b { color: #1B4332; }

/* Nota piccola */
.small-note {
    font-size: 0.9rem;
    color: #6B7D74;
    font-style: italic;
    margin-top: -0.6rem;
    margin-bottom: 1.6rem;
}

/* Divisore */
hr.divider {
    border: none;
    border-top: 1px solid #E0EDE4;
    margin: 3.2rem 0 2.4rem 0;
}

/* Card conclusioni */
.concl-card {
    background: #F7FBF8;
    border: 1px solid #E0EDE4;
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.concl-card b { color: #1B4332; }

footer {visibility: hidden;}

/* FIX MOBILE CENTRATURA E CONTENITORE GRAFICI */
@media (max-width: 640px) {
    .main .block-container {
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
        padding-top: 1.0rem !important;
    }
}

.stPlotlyChart {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.stPlotlyChart > div {
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}

# Helper per applicare sfondo bianco e testo scuro a tutti i grafici Plotly
def forza_sfondo_bianco(fig):
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1e293b")
    )
    return fig

# =========================================================
# CARICAMENTO E PULIZIA DATI
# =========================================================
@st.cache_data(show_spinner="Carico e preparo i dati energetici globali...")
def carica_dati():
    url = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
    df = pd.read_csv(url)

    # Rimuovo aggregati senza codice ISO (tranne Kosovo, che è un paese vero)
    finti = df[df["iso_code"].isna()]["country"].unique()
    da_rimuovere = [p for p in finti if p != "Kosovo"]
    df = df[~df["country"].isin(da_rimuovere)]

    # Tengo solo dal 2000 in poi
    df = df[df["year"] >= 2000]

    # Tengo solo i paesi con al massimo il 25% di dati mancanti su renewables_share_energy
    mancanti = df.groupby("country")["renewables_share_energy"].apply(lambda x: x.isna().sum())
    totale = df.groupby("country")["renewables_share_energy"].size()
    perc_mancante = (mancanti / totale * 100).round(1)
    paesi_da_tenere = perc_mancante[perc_mancante <= 25].index

    df = df[df["country"].isin(paesi_da_tenere)]
    return df


df = carica_dati()
ultimo_anno = df[df["renewables_share_energy"].notna()]["year"].max()

# =========================================================
# INTESTAZIONE
# =========================================================
st.markdown('<div class="hero-title">🌱 La Corsa alle Rinnovabili</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Un\'analisi globale su 79 paesi: chi guida davvero la transizione '
    'energetica, da cosa dipendiamo ancora e quanto conta essere ricchi quando si parla di energia.</div>',
    unsafe_allow_html=True
)

# =========================================================
# INDICE
# =========================================================
st.markdown("""
<div class="toc-grid">
    <a class="toc-card" href="#sezione-1">🏆 1. Chi vince la corsa alle rinnovabili</a>
    <a class="toc-card" href="#sezione-2">🇮🇹 2. L'Italia vs i grandi d'Europa</a>
    <a class="toc-card" href="#sezione-3">⚡ 3. Da cosa dipendiamo ancora</a>
    <a class="toc-card" href="#sezione-4">🌬️ 4. Solare vs eolico</a>
    <a class="toc-card" href="#sezione-5">💰 5. Ricchezza e consumo energetico</a>
    <a class="toc-card" href="#sezione-6">🗺️ 6. Il mondo in una mappa</a>
    <a class="toc-card" href="#conclusioni">📌 Conclusioni</a>
</div>
""", unsafe_allow_html=True)

# Parametri font e layout generali
title_font_size = 13 if IS_MOBILE else 17
legend_font_size = 9 if IS_MOBILE else 12

# =========================================================
# SEZIONE 1 — Chi vince la corsa alle rinnovabili
# =========================================================
st.header("1. Chi sta vincendo la corsa alle rinnovabili?", anchor="sezione-1")

st.markdown(
    '<div class="section-intro">Islanda e Norvegia dominano nettamente la classifica mondiale, '
    'superando il 70% di energia da fonti rinnovabili. Ma prima di incoronarle campionesse della '
    'transizione, vale la pena guardare da dove arriva quel primato.</div>',
    unsafe_allow_html=True
)

df_last = (
    df[(df["year"] == ultimo_anno) & (df["renewables_share_energy"] >= 25)]
    .dropna(subset=["renewables_share_energy"])
    .sort_values(by="renewables_share_energy", ascending=True)
    .reset_index(drop=True)
)

def assegna_colore(valore):
    if valore >= 70:
        return "#2F5D50"
    elif valore >= 50:
        return "#52796F"
    elif valore >= 30:
        return "#84A98C"
    else:
        return "#B7CDB5"

df_last["colore"] = df_last["renewables_share_energy"].apply(assegna_colore)

if IS_MOBILE:
    df_last["country_label"] = df_last["country"].str.replace("Dominican Republic", "Dom. Rep.")
else:
    df_last["country_label"] = df_last["country"]

fig1 = px.bar(
    df_last, x="renewables_share_energy", y="country_label", orientation="h",
    text="renewables_share_energy", color="colore", color_discrete_map="identity"
)

fig1_height = max(420, len(df_last) * 18) if IS_MOBILE else max(560, len(df_last) * 24)

max_val = df_last["renewables_share_energy"].max()

fig1.update_traces(
    texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False,
    textfont=dict(size=8.5 if IS_MOBILE else 11, color="#333333"), marker_line_width=0, width=0.65
)
fig1.update_layout(
    title={"text": f"<b>Chi guida la transizione<br>energetica ({ultimo_anno})</b>", "x": 0.0, "xanchor": "left", "font": dict(size=title_font_size)},
    xaxis_title="Quota di energia rinnovabile (%)", yaxis_title="",
    template="plotly_white", height=fig1_height, showlegend=False,
    margin=dict(l=5 if IS_MOBILE else 100, r=55 if IS_MOBILE else 80, t=55 if IS_MOBILE else 80, b=35)
)
fig1.update_xaxes(
    showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True,
    range=[0, max_val * 1.15 if IS_MOBILE else max_val * 1.1]
)
fig1.update_yaxes(
    showgrid=False, categoryorder="array", categoryarray=df_last["country_label"], 
    automargin=True, tickfont=dict(size=8.5 if IS_MOBILE else 11)
)
st.plotly_chart(forza_sfondo_bianco(fig1), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown(
    '<div class="small-note">I paesi in cima alla classifica sono spesso piccoli Stati con condizioni '
    'geografiche particolarmente favorevoli (risorse idroelettriche o geotermiche abbondanti). '
    'La quota di rinnovabili premia quindi anche la "fortuna geografica", non solo lo sforzo di transizione.</div>',
    unsafe_allow_html=True
)

paesi_leader = ["Iceland", "Norway", "Sweden", "Brazil", "Portugal", "Austria"]
trend = (
    df[(df["country"].isin(paesi_leader)) & (df["year"] >= 2000)]
    .dropna(subset=["renewables_share_energy"])
    .sort_values(["country", "year"])
)
palette_verde = ["#2F5D50", "#52796F", "#84A98C", "#A4C3B2", "#CAD2C5"]

fig2 = px.line(
    trend, x="year", y="renewables_share_energy", color="country",
    markers=True, color_discrete_sequence=palette_verde
)

fig2_height = 300 if IS_MOBILE else 580

fig2.update_traces(line=dict(width=2), marker=dict(size=5 if IS_MOBILE else 7))
fig2.update_layout(
    title={"text": "<b>Evoluzione della quota di rinnovabili<br>nei paesi leader</b>", "x": 0.0, "xanchor": "left", "font": dict(size=title_font_size)},
    xaxis_title="Anno", yaxis_title="Quota (%)",
    template="plotly_white", height=fig2_height, hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.38 if IS_MOBILE else -0.18, xanchor="center", x=0.5, title="", font=dict(size=legend_font_size)),
    margin=dict(l=10 if IS_MOBILE else 40, r=20 if IS_MOBILE else 40, t=55 if IS_MOBILE else 85, b=65 if IS_MOBILE else 90)
)
fig2.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
fig2.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
st.plotly_chart(forza_sfondo_bianco(fig2), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown(
    '<div class="insight-box">La classifica di oggi però non racconta tutta la storia: la '
    '<b>Danimarca</b>, pur non comparendo tra i primissimi, è il paese che ha guadagnato più terreno '
    'in assoluto, con un incremento di circa <b>+35 punti percentuali dal 2000</b> — seguita da Portogallo '
    'e Lituania. Quindi, chi vince davvero questa corsa? Non c\'è una risposta unica: Islanda e Norvegia '
    'dominano oggi grazie a risorse naturali che pochi altri hanno, ma la vera storia della transizione la '
    'scrivono paesi come Danimarca e Portogallo, partiti da zero e cresciuti più rapidamente di chiunque altro.</div>',
    unsafe_allow_html=True
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# =========================================================
# SEZIONE 2 — Italia vs Europa
# =========================================================
st.header("2. L'Italia come si posiziona rispetto ai grandi d'Europa?", anchor="sezione-2")

st.markdown(
    '<div class="section-intro">A livello mondiale l\'Italia è 38ª, un ritardo significativo rispetto '
    'ai paesi che guidano la transizione. Ma come se la cava rispetto ai suoi vicini più diretti — '
    'Germania, Francia e Spagna?</div>',
    unsafe_allow_html=True
)

countries_eu = ["Italy", "Germany", "France", "Spain"]
df_europe = df[(df["country"].isin(countries_eu)) & (df["year"] >= 2000)]
colori_paesi = {"Italy": "#1B4332", "Germany": "#74A57F", "France": "#95C99A", "Spain": "#B7D7B0"}

fig3 = px.line(
    df_europe, x="year", y="renewables_share_energy", color="country",
    markers=True, color_discrete_map=colori_paesi
)

fig3_height = 290 if IS_MOBILE else 550

fig3.update_traces(line=dict(width=2), marker=dict(size=5 if IS_MOBILE else 7))
fig3.update_traces(selector=dict(name="Italy"), line=dict(width=3), marker=dict(size=7 if IS_MOBILE else 9))
fig3.update_layout(
    title={"text": "<b>Italia vs grandi paesi europei</b>", "x": 0.0, "xanchor": "left", "font": dict(size=title_font_size)},
    xaxis_title="Anno", yaxis_title="Quota (%)",
    template="plotly_white", height=fig3_height, hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.38 if IS_MOBILE else -0.18, xanchor="center", x=0.5, title="", font=dict(size=legend_font_size)),
    margin=dict(l=10 if IS_MOBILE else 70, r=20 if IS_MOBILE else 50, t=50 if IS_MOBILE else 70, b=60 if IS_MOBILE else 90)
)
fig3.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
fig3.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
st.plotly_chart(forza_sfondo_bianco(fig3), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown(
    '<div class="insight-box">L\'Italia cresce in modo costante e si mantiene su livelli competitivi. '
    'Tuttavia il confronto mostra come <b>Germania</b> e soprattutto <b>Spagna</b> abbiano accelerato di più '
    'negli ultimi anni, mentre la <b>Francia</b> resta su valori più bassi — anche per il forte peso storico '
    'del nucleare nel suo mix energetico.</div>',
    unsafe_allow_html=True
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# =========================================================
# SEZIONE 3 — Mix energetico
# =========================================================
st.header("3. Da cosa dipendiamo ancora? Il mix energetico", anchor="sezione-3")

st.markdown(
    '<div class="section-intro">Sapere quanto pesano le rinnovabili è solo metà della storia. '
    'L\'altra metà è capire su cosa poggia ancora oggi il sistema energetico di ogni paese: un ritratto '
    'che rivela quanto ciascuno resti legato alle proprie scelte storiche.</div>',
    unsafe_allow_html=True
)

countries_mix = ["Iceland", "Norway", "Brazil", "France", "Germany", "Italy",
                  "China", "India", "Spain", "Austria", "Switzerland"]
df_mix = df[(df["country"].isin(countries_mix)) & (df["year"] == ultimo_anno)].copy()

fonti = {
    "renewables_share_energy": "Rinnovabili", "nuclear_share_energy": "Nucleare",
    "gas_share_energy": "Gas", "oil_share_energy": "Petrolio", "coal_share_energy": "Carbone"
}
mix = df_mix[["country"] + list(fonti.keys())].melt(id_vars="country", var_name="Fonte", value_name="Quota")
mix["Fonte"] = mix["Fonte"].map(fonti)

colori_mix = {
    "Rinnovabili": "#74C69D", "Nucleare": "#C0C6CC", "Gas": "#E9C46A",
    "Petrolio": "#6D6875", "Carbone": "#2F3B45"
}

fig4 = px.bar(mix, x="country", y="Quota", color="Fonte", text="Quota", color_discrete_map=colori_mix)

fig4_height = 340 if IS_MOBILE else 620

fig4.update_traces(texttemplate="%{text:.0f}%", textposition="inside", textfont=dict(size=8 if IS_MOBILE else 11))
fig4.update_layout(
    barmode="stack",
    title={"text": f"<b>Da cosa dipende ancora<br>il sistema energetico? ({ultimo_anno})</b>", "x": 0.0, "xanchor": "left", "font": dict(size=title_font_size)},
    xaxis_title="", yaxis_title="Quota mix (%)",
    template="plotly_white", height=fig4_height,
    legend=dict(orientation="h", yanchor="top", y=-0.42 if IS_MOBILE else -0.28, xanchor="center", x=0.5, title="", font=dict(size=legend_font_size)),
    margin=dict(l=10 if IS_MOBILE else 60, r=15 if IS_MOBILE else 30, t=55 if IS_MOBILE else 85, b=85 if IS_MOBILE else 110),
    uniformtext_minsize=6 if IS_MOBILE else 8, uniformtext_mode="hide"
)
fig4.update_xaxes(tickangle=-50 if IS_MOBILE else -40, automargin=True, tickfont=dict(size=8.5 if IS_MOBILE else 11))
fig4.update_yaxes(range=[0, 100], showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
st.plotly_chart(forza_sfondo_bianco(fig4), use_container_width=True, config=PLOTLY_CONFIG)

dipendenza_media = (
    df[df["year"] == ultimo_anno][list(fonti.keys())]
    .mean().rename(index=fonti).round(1)
)

st.markdown(
    f'<div class="insight-box">Il grafico mostra quanto la transizione non proceda in modo uniforme: '
    f'Islanda e Norvegia hanno un sistema quasi interamente rinnovabile, altri restano ancorati a fossili '
    f'e nucleare. A livello globale la dipendenza maggiore resta dal <b>petrolio</b> '
    f'({dipendenza_media["Petrolio"]:.1f}% in media) e dal <b>gas</b> ({dipendenza_media["Gas"]:.1f}%) — '
    f'insieme coprono ancora quasi due terzi del fabbisogno mondiale. Le <b>rinnovabili</b> si fermano in '
    f'media al {dipendenza_media["Rinnovabili"]:.1f}%, mentre il <b>nucleare</b> resta la fonte più marginale '
    f'({dipendenza_media["Nucleare"]:.1f}%), segno di quanto resti un tema controverso in molti paesi.</div>',
    unsafe_allow_html=True
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# =========================================================
# SEZIONE 4 — Solare vs eolico
# =========================================================
st.header("4. Chi cresce più in fretta tra solare ed eolico?", anchor="sezione-4")

st.markdown(
    '<div class="section-intro">Sono le due tecnologie di cui si parla di più quando si pensa al futuro '
    'dell\'energia pulita. Ma chi sta davvero correndo più veloce, e quanto pesano rispetto a tutte le '
    'altre fonti rinnovabili?</div>',
    unsafe_allow_html=True
)

andamento = (
    df.groupby("year")[["solar_share_energy", "wind_share_energy"]]
    .mean().reset_index()
    .melt(id_vars="year", var_name="Fonte", value_name="Quota media (%)")
    .dropna(subset=["Quota media (%)"])
)
andamento["Fonte"] = andamento["Fonte"].map({"solar_share_energy": "Solare", "wind_share_energy": "Eolico"})
colori_fonti = {"Solare": "#F4A261", "Eolico": "#457B9D"}

fig5 = px.line(andamento, x="year", y="Quota media (%)", color="Fonte", markers=True, color_discrete_map=colori_fonti)

fig5_height = 280 if IS_MOBILE else 550

fig5.update_traces(line=dict(width=2), marker=dict(size=5 if IS_MOBILE else 7))
fig5.update_layout(
    title={"text": "<b>Chi cresce più in fretta: solare o eolico?</b>", "x": 0.0, "xanchor": "left", "font": dict(size=title_font_size)},
    xaxis_title="Anno", yaxis_title="Quota media (%)",
    template="plotly_white", height=fig5_height, hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.35 if IS_MOBILE else -0.18, xanchor="center", x=0.5, title="", font=dict(size=legend_font_size)),
    margin=dict(l=10 if IS_MOBILE else 40, r=20 if IS_MOBILE else 40, t=50 if IS_MOBILE else 75, b=55 if IS_MOBILE else 90)
)
fig5.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
fig5.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
st.plotly_chart(forza_sfondo_bianco(fig5), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown(
    '<div class="small-note">L\'eolico è passato dallo 0,11% al 3,48% (+3,4 punti), il solare dallo 0,00% '
    'al 2,74% (+2,7 punti). L\'eolico era già una tecnologia minimamente diffusa nel 2000, mentre il solare '
    'partiva praticamente da zero — la sua crescita nasce quasi dal nulla in 25 anni, sostenuta dal crollo '
    'dei costi dei pannelli fotovoltaici nell\'ultimo decennio.</div>',
    unsafe_allow_html=True
)

fonti_rinnovabili = {
    "hydro_share_energy": "Idroelettrico", "solar_share_energy": "Solare", "wind_share_energy": "Eolico",
    "biofuel_share_energy": "Bioenergie", "other_renewables_share_energy": "Altre rinnovabili"
}
rinnovabili_media = (
    df[df["year"] == ultimo_anno][list(fonti_rinnovabili.keys())]
    .mean().rename(index=fonti_rinnovabili).sort_values(ascending=True).round(2).reset_index()
)
rinnovabili_media.columns = ["Fonte", "Quota media globale (%)"]

colori_rinnovabili = {
    "Idroelettrico": "#2A9D8F", "Solare": "#F4A261", "Eolico": "#457B9D",
    "Bioenergie": "#8D6A4B", "Altre rinnovabili": "#B0B0B0"
}

fig6 = px.bar(
    rinnovabili_media, x="Quota media globale (%)", y="Fonte", orientation="h",
    text="Quota media globale (%)", color="Fonte", color_discrete_map=colori_rinnovabili
)

fig6_height = 260 if IS_MOBILE else 450
max_val_r = rinnovabili_media["Quota media globale (%)"].max()

fig6.update_traces(
    texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False,
    marker_line_width=0, textfont=dict(size=8.5 if IS_MOBILE else 11)
)
fig6.update_layout(
    title={"text": f"<b>Quali rinnovabili<br>contano davvero? ({ultimo_anno})</b>", "x": 0.0, "xanchor": "left", "font": dict(size=title_font_size)},
    xaxis_title="Quota media (%)", yaxis_title="",
    template="plotly_white", height=fig6_height, showlegend=False, 
    margin=dict(l=5 if IS_MOBILE else 140, r=50 if IS_MOBILE else 100, t=55 if IS_MOBILE else 85, b=35 if IS_MOBILE else 50)
)
fig6.update_xaxes(
    showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True,
    range=[0, max_val_r * 1.2 if IS_MOBILE else max_val_r * 1.15]
)
fig6.update_yaxes(automargin=True, tickfont=dict(size=8.5 if IS_MOBILE else 11))
st.plotly_chart(forza_sfondo_bianco(fig6), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown(
    '<div class="insight-box">Nonostante la crescita rapida, solare ed eolico restano ancora dietro '
    'all\'<b>idroelettrico</b>, che con l\'8,1% è di gran lunga la fonte rinnovabile più diffusa al mondo — '
    'più del doppio dell\'eolico e quasi tre volte il solare. La "rivoluzione verde" raccontata dai media è '
    'soprattutto una rivoluzione di <i>crescita</i>, non ancora di <i>peso reale</i> sul totale.</div>',
    unsafe_allow_html=True
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# =========================================================
# SEZIONE 5 — Ricchezza e consumo pro capite
# =========================================================
st.header("5. I paesi ricchi consumano davvero più energia?", anchor="sezione-5")

st.markdown(
    '<div class="section-intro">Confrontiamo la ricchezza media per abitante con quanta energia consuma '
    'in media una singola persona, per capire se esiste davvero una relazione tra le due cose.</div>',
    unsafe_allow_html=True
)

df_gdp = (
    df.dropna(subset=["gdp", "energy_per_capita", "population"])
    .sort_values("year").groupby("country").tail(1).copy()
)
df_gdp["gdp_per_capita"] = df_gdp["gdp"] / df_gdp["population"]

soglia_popolazione = df_gdp["population"].sort_values(ascending=False).iloc[4]
df_gdp["etichetta"] = df_gdp.apply(
    lambda r: r["country"] if r["population"] >= soglia_popolazione else "", axis=1
)

fig7 = px.scatter(
    df_gdp, x="gdp_per_capita", y="energy_per_capita", size="population",
    hover_name="country", text="etichetta", log_x=True,
    color_discrete_sequence=["#40916C"]
)
fig7.update_traces(
    marker=dict(opacity=0.65, line=dict(width=0.5, color="white")),
    textposition="top center", textfont=dict(size=8 if IS_MOBILE else 11, color="#2F3B45")
)

log_x = np.log10(df_gdp["gdp_per_capita"])
coeff = np.polyfit(log_x, df_gdp["energy_per_capita"], 1)
x_linea = np.linspace(log_x.min(), log_x.max(), 100)
y_linea = coeff[0] * x_linea + coeff[1]

fig7.add_trace(go.Scatter(
    x=10 ** x_linea, y=y_linea, mode="lines",
    line=dict(color="#1B4332", width=2, dash="dash"),
    name="Tendenza", hoverinfo="skip", showlegend=False
))

fig7_height = 300 if IS_MOBILE else 580

fig7.update_layout(
    title={"text": "<b>Più ricchi, più energivori?</b>", "x": 0.0, "xanchor": "left", "font": dict(size=title_font_size)},
    xaxis_title="PIL pro capite ($)", yaxis_title="Consumo pro capite (kWh)",
    template="plotly_white", height=fig7_height,
    margin=dict(l=10 if IS_MOBILE else 40, r=20 if IS_MOBILE else 40, t=50 if IS_MOBILE else 75, b=35 if IS_MOBILE else 50)
)
fig7.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
fig7.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.12)", automargin=True)
st.plotly_chart(forza_sfondo_bianco(fig7), use_container_width=True, config=PLOTLY_CONFIG)

correlazione = df_gdp["gdp_per_capita"].corr(df_gdp["energy_per_capita"])

st.markdown(
    f'<div class="insight-box">Più un paese è ricco, più energia consuma ogni suo abitante — e non in modo '
    f'lineare, ma sempre più velocemente man mano che sale il reddito (correlazione di <b>{correlazione:.2f}</b>, '
    f'un legame forte). Attenzione però a non confondere due cose diverse: quanti abitanti ha un paese e '
    f'quanta energia consuma ciascuno di loro. Cina, India, Indonesia e Pakistan pesano moltissimo sul '
    f'consumo energetico <i>mondiale</i> per pura massa demografica, ma il consumo <i>pro capite</i> resta '
    f'contenuto perché il reddito medio è ancora basso. Gli Stati Uniti invece hanno sia tanta popolazione '
    f'sia un reddito alto, quindi ogni cittadino consuma molta energia. Il messaggio di fondo: la ricchezza '
    f'spinge il consumo a persona, ma il consumo energetico mondiale nel suo complesso dipende soprattutto '
    f'da quante persone vivono sulla Terra — due leve diverse che si sommano.</div>',
    unsafe_allow_html=True
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# =========================================================
# SEZIONE 6 — Mappa del mondo
# =========================================================
st.header("6. La transizione energetica vista dal mondo", anchor="sezione-6")

st.markdown(
    '<div class="section-intro">Per chiudere, un colpo d\'occhio su tutto il pianeta: quanto è diffusa oggi '
    'l\'energia rinnovabile, paese per paese.</div>',
    unsafe_allow_html=True
)

df_mappa = (
    df.dropna(subset=["renewables_share_energy", "iso_code"])
    .sort_values("year").groupby("country").tail(1).copy()
)
bins = [0, 15, 30, 50, 100]
etichette = ["0-15%", "15-30%", "30-50%", "50%+"]
df_mappa["fascia"] = pd.cut(df_mappa["renewables_share_energy"], bins=bins, labels=etichette)

colori_fasce = {"0-15%": "#D8F3DC", "15-30%": "#95D5B2", "30-50%": "#52B788", "50%+": "#1B4332"}

fig8 = px.choropleth(
    df_mappa, locations="iso_code", color="fascia", hover_name="country",
    hover_data={"renewables_share_energy": ":.1f", "fascia": False, "iso_code": False},
    color_discrete_map=colori_fasce, category_orders={"fascia": etichette}
)

fig8_height = 280 if IS_MOBILE else 600

fig8.update_traces(marker_line_color="#B0B0B0", marker_line_width=0.6)
fig8.update_layout(
    title={"text": "<b>La transizione energetica<br>vista dal mondo, oggi</b>", "x": 0.0, "xanchor": "left",
           "font": dict(size=title_font_size, color="#1B4332")},
    template="plotly_white", height=fig8_height, margin=dict(t=50 if IS_MOBILE else 90, b=40, l=0, r=0),
    geo=dict(
        showframe=False, showcoastlines=False, showland=True, landcolor="#f8fafc",
        showocean=True, oceancolor="#ffffff", showlakes=False, showcountries=True,
        countrycolor="#B0B0B0", projection_type="natural earth", bgcolor="#ffffff"
    ),
    paper_bgcolor="#ffffff",
    legend=dict(orientation="h", yanchor="bottom", y=-0.28 if IS_MOBILE else -0.1, xanchor="center", x=0.5, title="", font=dict(size=legend_font_size))
)
st.plotly_chart(forza_sfondo_bianco(fig8), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# =========================================================
# CONCLUSIONI
# =========================================================
st.header("📌 Conclusioni", anchor="conclusioni")

st.markdown(
    '<div class="section-intro">Mettendo insieme tutte le analisi, il quadro che emerge non è '
    '"il mondo si sta convertendo alle rinnovabili" né "il mondo dipende ancora troppo dai fossili" — '
    'sono vere entrambe le cose insieme, a seconda di dove si guarda.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="concl-card"><b>La transizione è reale ma profondamente diseguale.</b> Islanda e Norvegia '
    'superano il 70% grazie a risorse naturali che pochissimi altri paesi hanno; Danimarca e Portogallo '
    'dimostrano che una crescita rapida è possibile anche senza quel vantaggio. Ma la mappa finale lo '
    'conferma a colpo d\'occhio: gran parte del mondo, soprattutto Asia, Africa e Medio Oriente, resta '
    'ancora lontana da quote significative.</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="concl-card"><b>A livello globale, i fossili restano il vero pilastro.</b> Petrolio e gas '
    'coprono da soli quasi due terzi del mix energetico medio mondiale, contro appena il 17,4% delle '
    'rinnovabili. Anche i paesi "leader" sono eccezioni statistiche, non la norma.</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="concl-card"><b>Tra le rinnovabili, la vera storia è la crescita, non ancora il volume.</b> '
    'Solare ed eolico accelerano più di ogni altra fonte, ma restano dietro all\'idroelettrico — la '
    '"rivoluzione verde" raccontata dai media è soprattutto un fenomeno di velocità, non ancora di peso '
    'reale sul totale.</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="concl-card"><b>Ricchezza e popolazione tirano in direzioni diverse.</b> Il consumo pro '
    'capite è legato fortemente alla ricchezza di un paese, ma i giganti demografici come Cina, India, '
    'Indonesia e Pakistan dimostrano che avere tanti abitanti non equivale ad avere alti consumi a persona.'
    '</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="concl-card"><b>L\'Italia si colloca in una posizione intermedia:</b> 38ª a livello '
    'mondiale, con una crescita costante ma più lenta rispetto a Germania e Spagna, che negli ultimi anni '
    'hanno accelerato di più.</div>', unsafe_allow_html=True
)

st.markdown(
    '<p style="text-align:center; color:#6B7D74; margin-top:2.5rem; font-size:0.9rem;">'
    'Dati: Our World in Data — Energy Dataset · Elaborazione e grafici realizzati con Python, Pandas e Plotly</p>',
    unsafe_allow_html=True
)
