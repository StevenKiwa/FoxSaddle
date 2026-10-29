
import streamlit as st

from nucleo.graficas import graficas_duales

def inicio(ctx):
    f, a, b = ctx.f, ctx.a, ctx.b           
    st.write("Plataforma interactiva para aprender **límites** y **derivadas parciales** de funciones de dos "
             "variables, con cálculo simbólico, gráficas 2D y 3D, demostración formal ε-δ y "
             "explicaciones con inteligencia artificial.")
    st.info("Escribe una función en el editor de arriba, elige una sección y explora.")

    graficas_duales(f, a, b, 3)
