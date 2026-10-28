"""Sección Superficies de nivel: superficies w = f(x, y, z) = c."""
import streamlit as st
import sympy as sp

from nucleo.graficas import figura_nivel_3d, mostrar
from nucleo.ia import bloque_ia
from nucleo.matematica import leer


def superficies_nivel(ctx):
    """Dibuja varias superficies de nivel de una función de tres variables, entre dos niveles elegidos."""
    st.info("**Superficie de nivel:** lugar geométrico de todos los puntos (x, y, z) del dominio que originan "
            "iguales valores de la función w = f(x, y, z).")
    # Esta sección usa su PROPIA función w (de tres variables), distinta de la f(x, y) del editor de arriba.
    # `leer` la valida igual que a f: si el texto no es válido, el error lo muestra la página principal.
    texto_w = st.text_input("w = f(x, y, z) =", "x^2+y^2+z^2")
    w = leer(texto_w)
    st.latex(r"w=" + sp.latex(w))
    c1, c2, c3, c4 = st.columns(4)
    c_min = c1.number_input("Nivel mínimo", value=1.0)
    c_max = c2.number_input("Nivel máximo", value=9.0)
    n = c3.slider("Superficies", 1, 6, 3)         # máximo 6: cada una es una isosuperficie sobre 40³ puntos
    rango = c4.slider("Rango (unidades)", 1, 50, 3, 1)
    mostrar(figura_nivel_3d(w, c_min, c_max, n, rango))
    # Aquí no se usa ctx.base: w es otra función, el contexto de f(x, y) no aplica
    bloque_ia(f"Función w = {w}. Niveles entre {c_min} y {c_max}. Explica qué son sus superficies de nivel.", "ia_sn")