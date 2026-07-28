import streamlit as st
import nbformat
import plotly.graph_objects as go
import json

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Analisi Rinnovabili",
    page_icon="⚡",
    layout="wide"
)

# Stile CSS per rendere l'interfaccia elegante e moderna
st.markdown("""
    <style>
    .stApp {
        background-color: #F6F7FB;
        font-family: 'Inter', sans-serif;
    }
    
    h1 {
        color: #00A67E !important;
        font-weight: 700 !important;
    }
    
    h2 {
        color: #181C2A !important;
        border-bottom: 2px solid #E4E6F0;
        padding-bottom: 8px;
        margin-top: 30px !important;
    }

    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #E4E6F0;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_notebook():
    return nbformat.read("Rinnovabili.ipynb", as_version=4)

try:
    nb = load_notebook()
    
    for cell in nb.cells:
        # 1. TESTO MARKDOWN
        if cell.cell_type == "markdown":
            st.markdown(cell.source)
            
        # 2. GRAFICI E OUTPUT CODICE
        elif cell.cell_type == "code":
            for output in cell.get("outputs", []):
                if output.output_type in ["display_data", "execute_result"]:
                    data = output.get("data", {})
                    
                    # Grafico Plotly da dati JSON
                    if "application/vnd.plotly.v1+json" in data:
                        fig_dict = data["application/vnd.plotly.v1+json"]
                        fig = go.Figure(fig_dict)
                        # Forziamo il re-layout per adattarsi al 100% su qualsiasi schermo
                        fig.update_layout(
                            autosize=True,
                            margin=dict(l=15, r=15, t=40, b=40)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    # Contenuti HTML (Grafici salvati in HTML o Tabelle)
                    elif "text/html" in data:
                        html_content = "".join(data["text/html"]) if isinstance(data["text/html"], list) else data["text/html"]
                        
                        # Esclude tabelle tecniche con min/max/count
                        if "min" in html_content and "max" in html_content and "count" in html_content:
                            continue
                            
                        if "plotly" in html_content.lower():
                            st.components.v1.html(html_content, height=450, scrolling=False)
                        else:
                            st.markdown(html_content, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Impossibile leggere il notebook 'Rinnovabili.ipynb'. Assicurati che sia presente nella repository. Dettaglio: {e}")
