import streamlit as st
import nbformat
from markdown import markdown
import plotly.io as pio

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Analisi Rinnovabili",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stile CSS per un'estetica moderna, pulita e professionale
st.markdown("""
    <style>
    /* Sfondo e font generale */
    .stApp {
        background-color: #F6F7FB;
        font-family: 'Inter', sans-serif;
    }
    
    /* Titoli */
    h1 {
        color: #00A67E !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        padding-bottom: 10px;
    }
    
    h2 {
        color: #181C2A !important;
        border-bottom: 2px solid #E4E6F0;
        padding-bottom: 8px;
        margin-top: 30px !important;
    }

    /* Contenitore per i grafici */
    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #E4E6F0;
        margin-bottom: 25px;
    }
    
    /* Tabelle */
    div[data-testid="stTable"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #E4E6F0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_notebook():
    return nbformat.read("Rinnovabili.ipynb", as_version=4)

try:
    nb = load_notebook()
    
    for cell in nb.cells:
        # Renderizza il testo Markdown
        if cell.cell_type == "markdown":
            st.markdown(cell.source)
            
        # Renderizza gli Output del Codice (Grafici e Tabelle)
        elif cell.cell_type == "code":
            for output in cell.get("outputs", []):
                
                # Case 1: Grafici Plotly (JSON / Structure)
                if output.output_type in ["display_data", "execute_result"]:
                    data = output.get("data", {})
                    
                    # Se il grafico è in formato JSON Plotly
                    if "application/vnd.plotly.v1+json" in data:
                        fig_data = data["application/vnd.plotly.v1+json"]
                        fig = pio.from_json(pio.to_json(fig_data))
                        st.plotly_chart(fig, use_container_width=True)
                        
                    # Se il grafico/tabella è salvato in formato HTML
                    elif "text/html" in data:
                        html_content = "".join(data["text/html"]) if isinstance(data["text/html"], list) else data["text/html"]
                        
                        # Filtra eventuali tabelle di debug indesiderate
                        if "min" in html_content and "max" in html_content and "count" in html_content:
                            continue
                            
                        # Se contiene uno script Plotly
                        if "plotly" in html_content.lower():
                            st.components.v1.html(html_content, height=480, scrolling=False)
                        else:
                            st.markdown(html_content, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Errore nel caricamento del file notebook 'Rinnovabili.ipynb': {e}")
