"""Sección Gráfica 2D y 3D: el mismo ejercicio en el plano xy y como superficie 3D, con rango ajustable."""
import streamlit as st

from nucleo.graficas import graficas_duales


def grafica_2d_3d(ctx):
    """Dibuja f en dos vistas lado a lado (2D y 3D) con el rango que elija el usuario."""
    f, a, b = ctx.f, ctx.a, ctx.b            # función y punto (a, b) elegidos por el usuario
    # Rango = cuántas unidades se grafican alrededor de (a, b). Hasta 50 de 1 en 1; con rangos grandes la
    # gráfica 3D se agranda sola (ver graficas.py) para que los números de los ejes sigan legibles.
    rango = st.slider("Rango de visualización (unidades)", 1, 50, 3, 1)
    graficas_duales(f, a, b, rango)
    st.caption("Gira con el mouse, acerca con la rueda. Ejes: x magenta, y lima, z cian. Punto lima: (a, b, f(a,b)).")