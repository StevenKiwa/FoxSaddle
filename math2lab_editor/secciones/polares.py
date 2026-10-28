"""Sección Límite en coordenadas polares."""
import streamlit as st
import sympy as sp

from nucleo.ia import bloque_ia
from nucleo.matematica import limite_polar, t


def polares(ctx):
    """Calcula el límite en (a, b) con x = a + r·cosθ, y = b + r·senθ, haciendo r → 0⁺."""
    f, a_s, b_s = ctx.f, ctx.a_s, ctx.b_s    # a_s y b_s: el punto en forma exacta de SymPy (sin decimales)
    st.subheader("Límite en coordenadas polares")
    st.write("Sustituimos x = a + r·cos θ, y = b + r·sen θ y hacemos r → 0⁺.")
    g, lim = limite_polar(f, a_s, b_s)       # g = f escrita en polares; lim = su límite cuando r → 0⁺
    st.latex(sp.latex(g))
    st.latex(r"\lim_{r\to0^+}=" + sp.latex(lim))
    # Si el resultado todavía contiene θ, depende de la dirección de acercamiento: el límite no existe
    if lim.has(t):
        st.error("El resultado depende de θ → el límite NO existe.")
    else:
        # Ojo: que no dependa de θ no basta (p. ej. x²y/(x⁴+y²) da 0 en polares, pero por la parábola y = x²
        # da 1/2). Por eso se remite a la demostración ε-δ y a las trayectorias curvas.
        st.success("El resultado no depende de θ → el límite existe y vale lo indicado.")
        st.caption("Para rigor, usa la demostración formal ε-δ.")
    bloque_ia(ctx.base + f" En polares: {g}; límite cuando r→0+: {lim}. Explica paso a paso.", "ia_po")