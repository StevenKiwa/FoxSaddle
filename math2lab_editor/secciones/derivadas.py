
import streamlit as st
import sympy as sp

from nucleo.graficas import graficas_duales
from nucleo.ia import bloque_ia
from nucleo.matematica import derivadas_parciales


def derivadas(ctx):
   
    f, a, b = ctx.f, ctx.a, ctx.b
    st.subheader("Derivadas parciales")
    fx, fy = derivadas_parciales(f)          
    st.latex(r"\frac{\partial f}{\partial x}=" + sp.latex(fx))
    st.latex(r"\frac{\partial f}{\partial y}=" + sp.latex(fy))
    graficas_duales(f, a, b, 3)              

    bloque_ia(ctx.base + f" fx = {fx}, fy = {fy}. Explica cómo se obtuvieron paso a paso.", "ia_de")
