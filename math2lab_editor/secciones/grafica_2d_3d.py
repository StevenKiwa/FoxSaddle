
import streamlit as st

from nucleo.graficas import graficas_duales


def grafica_2d_3d(ctx):

    f, a, b = ctx.f, ctx.a, ctx.b            
    rango = st.slider("Rango de visualización (unidades)", 1, 50, 3, 1)
    graficas_duales(f, a, b, rango)
    st.caption("Gira con el mouse, acerca con la rueda (en el celular, toca « Mover la gráfica»). "
               "Ejes: x magenta, y lima, z cian. Punto lima: (a, b, f(a,b)).")
