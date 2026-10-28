"""Sección Derivadas parciales ∂f/∂x y ∂f/∂y."""
import streamlit as st
import sympy as sp

from nucleo.graficas import graficas_duales
from nucleo.ia import bloque_ia
from nucleo.matematica import derivadas_parciales


def derivadas(ctx):
    """Muestra las derivadas parciales de f (calculadas con SymPy), la gráfica y una explicación opcional con IA."""
    f, a, b = ctx.f, ctx.a, ctx.b
    st.subheader("Derivadas parciales")
    fx, fy = derivadas_parciales(f)          # SymPy deriva y simplifica (el resultado queda en caché)
    st.latex(r"\frac{\partial f}{\partial x}=" + sp.latex(fx))
    st.latex(r"\frac{\partial f}{\partial y}=" + sp.latex(fy))
    graficas_duales(f, a, b, 3)              # rango fijo: la sección se centra en las fórmulas
    # La IA recibe fx y fy ya calculados: solo los explica, así no puede inventar el resultado
    bloque_ia(ctx.base + f" fx = {fx}, fy = {fy}. Explica cómo se obtuvieron paso a paso.", "ia_de")