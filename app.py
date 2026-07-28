import streamlit as st
import streamlit.components.v1 as components
import re
import nbformat
from markdown import markdown

# Configurazione della pagina Streamlit per occupare tutto lo schermo
st.set_page_config(
    page_title="Analisi Rinnovabili",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Rimuove i margini predefiniti di Streamlit per far combaciare l'HTML al 100%
st.markdown("""
    <style>
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def generate_exact_html():
    nb = nbformat.read("Rinnovabili.ipynb", as_version=4)

    def clean_md(text):
        if not text: return ""
        return re.sub(r'[\*\#]', '', text).strip()

    def get_emoji(text):
        t = text.lower()
        if "1." in t or "vincendo" in t: return "🏆"
        elif "2." in t or "italia" in t: return "🇮🇹"
        elif "3." in t or "dipendiamo" in t or "mix" in t: return "⚡"
        elif "4." in t or "fretta" in t or "solare" in t or "eolico" in t: return "☀️"
        elif "5." in t or "consumo" in t or "pro capite" in t: return "💡"
        elif "transazione" in t or "transizione" in t or "mondo" in t: return "🌍"
        elif "conclusioni" in t or "conclusione" in t: return "📌"
        return "📊"

    first_cell_idx = 0
    raw_title, raw_subtitle = "", ""

    for idx, cell in enumerate(nb.cells):
        source = cell.source if isinstance(cell.source, str) else "".join(cell.source)
        if source.strip():
            first_cell_idx = idx
            lines = [line.strip() for line in source.strip().split("\n") if line.strip()]
            if lines:
                raw_title = clean_md(lines[0])
                if len(lines) > 1: raw_subtitle = clean_md(" ".join(lines[1:]))
            break

    toc_items = []
    start_export = False
    IGNORE_TITLES = ["il messaggio di fondo", "messaggio di fondo", "nota", "note"]

    for cell in nb.cells[first_cell_idx + 1 :]:
        source = cell.source if isinstance(cell.source, str) else "".join(cell.source)
        if cell.cell_type == "markdown":
            if not start_export and "1. Chi sta vincendo" in source: start_export = True
            if start_export:
                headings = re.findall(r"^(?:#{1,3}\s*|\*\*\d+\.|\d+\.)\s*(.+)$", source, flags=re.MULTILINE)
                if not headings: headings = re.findall(r"^\*\*(.+?)\*\*", source, flags=re.MULTILINE)
                for h_text in headings:
                    clean_text = clean_md(h_text)
                    if any(ign in clean_text.lower() for ign in IGNORE_TITLES): continue
                    if clean_text and len(clean_text) > 3:
                        anchor_id = re.sub(r"[^\w\s-]", "", clean_text.lower()).replace(" ", "-").strip("-")
                        toc_items.append((clean_text, anchor_id, get_emoji(clean_text)))

    seen = set()
    unique_toc_items = [item for item in toc_items if not (item[1] in seen or seen.add(item[1]))]

    indice_html = '<div id="indice">\n  <h2>📑 INDICE</h2>\n  <ul>\n'
    for title, anchor, emoji in unique_toc_items:
        indice_html += f'    <li><a href="#{anchor}">{emoji} {title}</a></li>\n'
    indice_html += '  </ul>\n</div>\n'

    html_header = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{raw_title}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
:root{{ --bg:#F6F7FB; --card:#FFFFFF; --card-border:#E4E6F0; --primary:#00A67E; --text:#181C2A; --text-dim:#5C6274; --border:#E4E6F0; --shadow:0 20px 45px rgba(30,30,60,.08); --grad: linear-gradient(120deg, #00A67E 0%, #00C49A 100%); }}
*{{ box-sizing:border-box; }}

/* STILE BASE (ORIGINALE PER COMPUTER) */
body{{ 
    background: radial-gradient(circle at 15% 0%, rgba(0,166,126,.08), transparent 40%), radial-gradient(circle at 90% 10%, rgba(15,169,140,.07), transparent 45%), var(--bg); 
    font-family:'Inter',sans-serif; 
    max-width:1100px; 
    margin:auto; 
    padding:30px 30px 80px; 
    color:var(--text); 
    line-height:1.75; 
    font-size:18px; 
}}

h1,h2,h3{{ font-family:'Space Grotesk',sans-serif; scroll-margin-top: 40px; }}
.intro{{ background:transparent; padding:10px 0; width:100%; }}
.intro .eyebrow{{ display:inline-block; font-size:11px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:var(--primary); background:rgba(0,166,126,.10); border:1px solid rgba(0,166,126,.25); padding:5px 14px; border-radius:999px; margin-bottom:12px; }}
.intro h1{{ margin:0; font-size:48px; font-weight:700; letter-spacing:-1px; line-height:1.15; background:var(--grad); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
.intro .subtitle{{ font-size:16px; font-style: italic; color:var(--text-dim); margin-top:10px; max-width:850px; font-weight:400; line-height:1.6; opacity: 0.9; }}

.header-divider {{ border: none; height: 2px; background: linear-gradient(90deg, rgba(0,166,126,0.5) 0%, rgba(228,230,240,0.4) 70%, transparent 100%); margin: 15px 0 25px 0; }}

#indice{{ background:var(--card); border:1px solid var(--card-border); border-radius:18px; padding:20px; margin:0 0 35px; box-shadow:var(--shadow); }}
#indice h2{{ margin:0 0 16px 0!important; font-size:12px!important; font-weight:700!important; letter-spacing:1.5px; text-transform:uppercase; color:var(--text-dim)!important; border:none!important; padding:0!important; }}
#indice ul{{ list-style:none; margin:0; padding:0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:12px 20px; }}
#indice li{{ margin:0; }}
#indice a{{ color:var(--text); font-weight:600; font-size:14px; text-decoration:none; display:flex; align-items:center; gap:8px; transition:.2s ease; cursor:pointer; }}
#indice a:before{{ content:"→"; color:var(--primary); font-weight:700; }}
#indice a:hover{{ color:var(--primary); transform:translateX(3px); }}

.testo{{ margin:25px 0; color:var(--text-dim); word-wrap: break-word; }}
.testo strong{{ color:var(--text); font-weight:600; }}

.grafico{{ background:var(--card); padding:20px; margin:40px 0; border-radius:20px; box-shadow:var(--shadow); border:1px solid var(--card-border); position:relative; width:100%; overflow:hidden; }}
.grafico:before{{ content:""; position:absolute; top:0; left:0; right:0; height:4px; background:var(--grad); }}
.grafico .plotly-graph-div {{ width: 100% !important; height: auto !important; margin: 0 auto !important; }}
.grafico svg {{ max-width: 100% !important; }}

h2{{ margin-top:60px; margin-bottom:20px; font-size:28px; font-weight:700; color:var(--text); border-bottom:1px solid var(--border); padding-bottom:12px; }}

table{{ width:100%; border-collapse:collapse; margin:25px 0; background:var(--card); box-shadow:var(--shadow); border-radius:14px; overflow-x:auto; display:block; border:1px solid var(--card-border); }}
th{{ background:rgba(0,166,126,.10); color:var(--text); padding:12px 14px; font-weight:600; text-align:left; }}
td{{ padding:12px 14px; border-bottom:1px solid var(--border); color:var(--text-dim); }}
tr:nth-child(even){{ background:rgba(20,20,50,.02); }}

/* STILE SPECIFICO E LEGGERO PER CELLULARE (<768px) */
@media (max-width: 767px) {{
    body {{ 
        padding: 12px 8px 40px !important; 
        font-size: 14px !important;
        line-height: 1.5 !important;
    }}
    .intro h1 {{ font-size: 26px !important; }}
    .intro .subtitle {{ font-size: 13px !important; }}
    
    .grafico {{ 
        padding: 8px 4px !important; 
        margin: 20px 0 !important; 
        border-radius: 12px !important;
    }}
    .modebar-container {{ display: none !important; }}
    .testo {{ font-size: 14px !important; margin: 15px 0 !important; }}
    h2 {{ font-size: 20px !important; margin-top: 35px !important; }}
}}
</style>
</head>
<body>
<div class="intro">
    <span class="eyebrow">REPORT · DATA ANALYSIS</span>
    <h1>{raw_title}</h1>
    <p class="subtitle">{raw_subtitle}</p>
</div>
<hr class="header-divider">
{indice_html}
"""

    html_footer = """
<script>
// Scroll smooth per l'indice
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('#indice a').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var targetId = this.getAttribute('href').substring(1);
            var targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Adattamento dinamico dei grafici
function adaptPlotlyCharts() {
    var plots = document.querySelectorAll('.plotly-graph-div');
    var isMobile = window.innerWidth < 768;
    plots.forEach(function(p) {
        if (p._fullLayout) {
            if (isMobile) {
                // Configurazione compatta per Cellulare
                Plotly.relayout(p, {
                    'autosize': true,
                    'yaxis.automargin': true,
                    'xaxis.automargin': true,
                    'font.size': 10,
                    'title.font.size': 12,
                    'margin.l': 10,
                    'margin.r': 10,
                    'margin.t': 45,
                    'margin.b': 25
                });
            } else {
                // Configurazione ORIGINALE per Computer
                Plotly.relayout(p, {
                    'autosize': true,
                    'yaxis.automargin': true,
                    'xaxis.automargin': true,
                    'font.size': 13,
                    'title.font.size': 16,
                    'margin.l': 50,
                    'margin.r': 30,
                    'margin.t': 50,
                    'margin.b': 50
                });
            }
            Plotly.Plots.resize(p);
        }
    });
}
window.addEventListener('load', function() {
    var checkExist = setInterval(function() {
        var plots = document.querySelectorAll('.plotly-graph-div');
        if (plots.length > 0 && plots[0]._fullLayout) {
            adaptPlotlyCharts();
            clearInterval(checkExist);
        }
    }, 150);
});
window.addEventListener('resize', adaptPlotlyCharts);
</script>
</body>
</html>
"""

    body_content = ""
    start_export = False

    for cell in nb.cells[first_cell_idx + 1 :]:
        source = cell.source if isinstance(cell.source, str) else "".join(cell.source)
        if not start_export:
            if cell.cell_type == "markdown" and "1. Chi sta vincendo" in source: start_export = True
            else: continue

        if cell.cell_type == "markdown":
            lines = source.split("\n")
            new_lines = []
            for line in lines:
                h_match = re.match(r"^(#{1,3}|\*\*)\s*(.+?)\x2a*$", line)
                if h_match and ("1." in line or "2." in line or "3." in line or "4." in line or "5." in line or "Conclusioni" in line):
                    clean_t = clean_md(line)
                    anchor_id = re.sub(r"[^\w\s-]", "", clean_t.lower()).replace(" ", "-").strip("-")
                    new_lines.append(f'<h2 id="{anchor_id}">{clean_t}</h2>')
                else:
                    new_lines.append(line)
            formatted_source = "\n".join(new_lines)
            testo_html = markdown(formatted_source, extensions=["fenced_code", "tables"])
            body_content += f'<div class="testo">{testo_html}</div>\n'

        elif cell.cell_type == "code":
            for output in cell.get("outputs", []):
                if output.output_type in ["display_data", "execute_result"]:
                    data = output.get("data", {})
                    if "text/html" in data:
                        grafico_html = "".join(data["text/html"]) if isinstance(data["text/html"], list) else data["text/html"]
                        grafico_html = re.sub(r'style="[^"]*"', '', grafico_html)
                        if "min" in grafico_html and "max" in grafico_html and "count" in grafico_html:
                            if "plotly" in grafico_html.lower(): grafico_html = re.sub(r'<table[\s\S]*?</table>', '', grafico_html)
                            else: continue
                        body_content += f'<div class="grafico">{grafico_html}</div>\n'

    return html_header + body_content + html_footer

# Genera e carica l'HTML completo
html_code = generate_exact_html()
components.html(html_code, height=4500, scrolling=True)
