import json
import re
from functools import lru_cache
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from plotly.utils import PlotlyJSONEncoder

CARPETA = Path(__file__).resolve().parent / "visor_frontend"


def _rellenar(plantilla, valores):
    return re.sub(r"__([A-Z]+)__", lambda m: valores.get(m.group(1), m.group(0)), plantilla)


@lru_cache(maxsize=1)
def _plantilla():
    def leer(nombre):
        return (CARPETA / nombre).read_text(encoding="utf-8")
    return _rellenar(leer("visor.html"), {"CSS": leer("visor.css"), "JS": leer("visor.js")})


def _extraer_botones(fig):
    botones = []
    for menu in fig.to_plotly_json()["layout"].get("updatemenus", []) or []:
        for b in menu.get("buttons", []):
            botones.append({"label": b.get("label", ""), "metodo": b.get("method", "restyle"),
                            "args": b.get("args", []), "args2": b.get("args2")})
    return botones


def _mostrar_html(html, alto):
    if hasattr(st, "iframe"):
        st.iframe(html, width="stretch", height=alto)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=alto, scrolling=False)


def visor_plotly(fig, altura):
    botones = _extraer_botones(fig)
    limpia = go.Figure(fig)
    limpia.layout.updatemenus = []
    if "scene" not in fig.to_plotly_json()["layout"]:
        limpia.layout.dragmode = "pan"
    cuerpo = limpia.to_html(full_html=False, include_plotlyjs="cdn", div_id="grafica", default_width="100%",
                            default_height=f"{altura}px",
                            config={"displayModeBar": False, "displaylogo": False, "responsive": True,
                                    "doubleClick": False})
    botones_js = json.dumps(botones, cls=PlotlyJSONEncoder).replace("</", "<\\/")
    html = _rellenar(_plantilla(), {"GRAFICA": cuerpo, "ALTURA": str(int(altura)), "BOTONES": botones_js})
    _mostrar_html(html, int(altura) + 6)
