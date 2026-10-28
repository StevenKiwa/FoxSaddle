
from pathlib import Path

import streamlit as st
import sympy as sp
from PIL import Image


st.set_page_config(page_title="FoxSaddle", layout="wide",
                   page_icon=Image.open(Path(__file__).parent / "assets" / "foxsaddle_icono.png"))

from nucleo.contexto import Contexto
from nucleo.editor_formula import editor_formula
from nucleo.latex import latex_a_texto, texto_a_latex
from nucleo.marca import NOMBRE, logo_html
from nucleo.matematica import leer
from nucleo.tema import aplicar_css
from nucleo.tutorial import empezar_tutorial, tutorial
from secciones import SECCIONES

FORMULA_INICIAL = "x^2*y/(x^2+y^2)"


st.session_state.setdefault("texto_f", FORMULA_INICIAL)
st.session_state.setdefault("latex_f", texto_a_latex(leer(FORMULA_INICIAL)))
st.session_state.setdefault("ver_editor", 0)      
st.session_state.setdefault("error_formula", None)
st.session_state.setdefault("a", 0.0)
st.session_state.setdefault("b", 0.0)


def desde_texto():
    """Alternativa: el usuario escribe la fórmula como texto; se valida y se refleja en el editor."""
    texto = st.session_state.texto_alt.strip()
    if not texto:
        return
    try:
        f = leer(texto)
        st.session_state.latex_f = texto_a_latex(f)
    except Exception as e:
        st.session_state.error_formula = str(e)
        return
    st.session_state.texto_f = texto
    st.session_state.ver_editor += 1
    st.session_state.error_formula = None


aplicar_css()
st.sidebar.markdown(logo_html(), unsafe_allow_html=True)       
seccion = st.sidebar.radio("Sección", list(SECCIONES), key="seccion")
st.sidebar.markdown("---")
a = st.sidebar.number_input("Punto a (x → a)", key="a")
b = st.sidebar.number_input("Punto b (y → b)", key="b")
st.sidebar.button("❓ Ver tutorial", on_click=empezar_tutorial, key="btn_tutorial")

st.title(NOMBRE)
tutorial()

st.markdown("##### Escribe tu función  f(x, y)")
valor = editor_formula(st.session_state.latex_f, st.session_state.ver_editor)
if valor and valor.get("n") != st.session_state.get("n_editor"):      
    st.session_state.n_editor = valor["n"]
    try:
        st.session_state.texto_f = latex_a_texto(valor["latex"])
        leer(st.session_state.texto_f)                                 
        st.session_state.latex_f = valor["latex"]
        st.session_state.error_formula = None
    except Exception as e:
        st.session_state.error_formula = str(e)

with st.expander("¿Prefieres escribirla como texto? (alternativa)"):
    st.text_input("f(x, y) =", key="texto_alt", placeholder="x^2*y/(x^2+y^2)", on_change=desde_texto)
    st.caption("Potencias con ^ · raiz( ) · sen( ) cos( ) tan( ) · ln( ) · exp( ) · abs( ) · pi")

if st.session_state.error_formula:
    st.error(f"No pude leer la función: {st.session_state.error_formula}")
    st.stop()

texto_f = st.session_state.texto_f
f = leer(texto_f)
ctx = Contexto(f=f, a=a, b=b, a_s=sp.nsimplify(a), b_s=sp.nsimplify(b), texto_f=texto_f)

try:
    SECCIONES[seccion](ctx)
except Exception as e:
    st.error(f"Ocurrió un error en esta sección: {e}")
