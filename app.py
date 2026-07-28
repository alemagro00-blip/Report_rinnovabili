import streamlit as st
import nbformat
import plotly.graph_objects as go

st.set_page_config(page_title="Analisi Rinnovabili", page_icon="⚡", layout="wide")

st.markdown('''
    <style>
    .main { background-color: #F6F7FB; }
    h1 { color: #00A67E; }
    </style>
''', unsafe_allow_html=True)

@st.cache_data
def load_notebook():
    return nbformat.read("Rinnovabili.ipynb", as_version=4)

try:
    nb = load_notebook()
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            st.markdown(cell.source)
        elif cell.cell_type == "code":
            for output in cell.get("outputs", []):
                if output.output_type in ["display_data", "execute_result"]:
                    data = output.get("data", {})
                    if "application/vnd.plotly.v1+json" in data:
                        fig = go.Figure(data["application/vnd.plotly.v1+json"])
                        st.plotly_chart(fig, use_container_width=True)
                    elif "text/html" in data:
                        html_content = "".join(data["text/html"]) if isinstance(data["text/html"], list) else data["text/html"]
                        if "min" not in html_content and "count" not in html_content:
                            st.components.v1.html(html_content, height=450, scrolling=True)
except Exception as e:
    st.error(f"Carica il file Rinnovabili.ipynb nella cartella del progetto! Errore: {e}")
