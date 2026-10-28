"""Sección Inicio: presentación de la plataforma y las dos gráficas (2D y 3D) del ejercicio."""
import streamlit as st

from nucleo.graficas import graficas_duales


def inicio(ctx):
    """Pantalla de bienvenida: explica la plataforma y dibuja la función elegida en dos vistas."""
    f, a, b = ctx.f, ctx.a, ctx.b            # función y punto (a, b) elegidos por el usuario
    st.write("Plataforma interactiva para aprender **límites** y **derivadas parciales** de funciones de dos "
             "variables, con cálculo simbólico, gráficas 2D y 3D, demostración formal ε-δ y "
             "explicaciones con inteligencia artificial.")
    st.info("Escribe una función en el editor de arriba, elige una sección y explora.")
    # Rango fijo (3): aquí es solo una vista previa; el rango ajustable está en «Gráfica 2D y 3D»
    graficas_duales(f, a, b, 3)