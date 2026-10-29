
import streamlit as st
import sympy as sp

from nucleo.graficas import figura_curvas, mostrar
from nucleo.ia import bloque_ia


def curvas_nivel(ctx):

    f, a, b = ctx.f, ctx.a, ctx.b
    st.info("**Curva de nivel:** lugar geométrico de todos los puntos (x, y) del dominio que originan iguales "
            "valores de la función z = f(x, y).")
    c1, c2 = st.columns(2)
    n = c1.slider("Cantidad de curvas", 3, 40, 15)
    rango = c2.slider("Rango (unidades)", 1, 50, 3, 1)
    c = None                                  
    if st.checkbox("Mostrar solo una curva f(x, y) = c"):
        c = st.number_input("Valor de c", value=1.0)
        st.latex(sp.latex(sp.Eq(f, sp.nsimplify(c))))     
    mostrar(figura_curvas(f, a, b, rango, n, c))
    bloque_ia(ctx.base + " Explica qué son las curvas de nivel de esta función y cómo interpretarlas.", "ia_cn")
