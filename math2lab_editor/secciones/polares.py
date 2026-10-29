
import streamlit as st
import sympy as sp

from nucleo.ia import bloque_ia
from nucleo.matematica import limite_polar, t


def polares(ctx):

    f, a_s, b_s = ctx.f, ctx.a_s, ctx.b_s   
    st.subheader("Límite en coordenadas polares")
    st.write("Sustituimos x = a + r·cos θ, y = b + r·sen θ y hacemos r → 0⁺.")
    g, lim = limite_polar(f, a_s, b_s)       
    st.latex(sp.latex(g))
    st.latex(r"\lim_{r\to0^+}=" + sp.latex(lim))

    if lim.has(t):
        st.error("El resultado depende de θ → el límite NO existe.")
    else:
    
        st.success("El resultado no depende de θ → el límite existe y vale lo indicado.")
        st.caption("Para rigor, usa la demostración formal ε-δ.")
    bloque_ia(ctx.base + f" En polares: {g}; límite cuando r→0+: {lim}. Explica paso a paso.", "ia_po")
