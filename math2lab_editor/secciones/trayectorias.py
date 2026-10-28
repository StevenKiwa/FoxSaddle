"""Sección Límite por trayectorias: acercarse al punto por distintos caminos."""
import streamlit as st
import sympy as sp

from nucleo.ia import bloque_ia
from nucleo.matematica import limite_camino, s


def trayectorias(ctx):
    """Calcula el límite de f a lo largo de varios caminos hacia (a, b); si dos difieren, el límite no existe."""
    f, a_s, b_s = ctx.f, ctx.a_s, ctx.b_s
    st.subheader("Límite por trayectorias")
    st.write("Sustituimos x = a + s, y = b + trayectoria(s) y hacemos s → 0.")
    m = st.slider("Pendiente m de la recta y − b = m(x − a)", -5.0, 5.0, 1.0, 0.5)
    # Cada camino se da como la variación de y respecto a b (con x = a + s). Se incluye una parábola porque hay
    # funciones (como x²y/(x⁴+y²)) que valen 0 por todas las rectas y aun así no tienen límite.
    caminos = {f"recta de pendiente m = {m}": m * s, "parábola y − b = (x − a)²": s**2,
               "recta y − b = 0": 0 * s, "recta y − b = −(x − a)": -s}
    resultados, omitidos = {}, []
    for nombre, p in caminos.items():
        g, v = limite_camino(f, a_s, b_s, p)     # g = f sobre el camino; v = su límite cuando s → 0 (con caché)
        # Si f no está definida en NINGÚN punto del camino (p. ej. sen(xy)/(xy) sobre el eje x, donde xy = 0),
        # SymPy devuelve nan o zoo. Ese camino no dice nada sobre el límite: se omite en vez de compararlo.
        if g.has(sp.nan, sp.zoo):
            omitidos.append(nombre)
            st.write(f"**{nombre}:** f no está definida sobre este camino, así que se omite.")
            continue
        resultados[nombre] = v
        st.latex(rf"\text{{{nombre}}}:\ \lim_{{s\to0}} {sp.latex(g)} = {sp.latex(v)}")
    # Se simplifica antes de comparar para que valores equivalentes (p. ej. 1/2 y 0.5) cuenten como iguales
    if not resultados:
        st.warning("f no está definida sobre ninguno de los caminos probados. Prueba con otra función o punto.")
    elif len({sp.simplify(v) for v in resultados.values()}) > 1:
        st.error("Valores distintos por distintas trayectorias → el límite NO existe.")
    else:
        st.success("Todas las trayectorias coinciden. Esto sugiere (pero no demuestra) que el límite existe.")
        if omitidos:
            st.caption(f"Se omitieron {len(omitidos)} camino(s) donde f no está definida.")
    resumen = "; ".join(f"{nombre}: {v}" for nombre, v in resultados.items())
    if omitidos:                                 # la IA debe saber qué caminos no se pudieron usar
        resumen += ". Caminos omitidos porque f no está definida sobre ellos: " + ", ".join(omitidos)
    bloque_ia(ctx.base + " Resultados por trayectorias: " + resumen + ". Explica la conclusión.", "ia_tr")