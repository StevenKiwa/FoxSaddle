"""Gráficas Plotly: superficie 3D, mapa 2D, curvas de nivel y superficies de nivel, con ejes x, -x, y, -y, z, -z."""
from functools import lru_cache

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from nucleo.matematica import evaluar
from nucleo.visor import visor_plotly
from nucleo.tema import (
    CELESTE_NEON, CIAN, ESCALA_LINEAS, ESCALA_NEON, ETIQUETAS, FONDO, GRILLA, LIMA, MAGENTA, OPACIDAD_3D, PANEL,
    TEXTO)


def _ticks(r, eje_x=True):
    """Marcas de 1 en 1 (ningún número se salta). Con rangos grandes se achica y gira el texto para que quepan."""
    span = abs(r[1] - r[0])
    return dict(dtick=1, tick0=0, tickformat="d", tickfont=dict(size=12 if span <= 20 else 9),
                tickangle=-90 if (eje_x and span > 20) else 0)


def _boton_decimales(fig, ejes):
    """Botón (esquina inferior derecha de la gráfica) que alterna entre enteros y decimales en los ejes."""
    con, sin = {}, {}
    for e in ejes:
        con.update({f"{e}.dtick": 0.5, f"{e}.tickformat": ".1f"})
        sin.update({f"{e}.dtick": 1, f"{e}.tickformat": "d"})
    fig.update_layout(updatemenus=[dict(
        type="buttons", direction="left", showactive=False, active=-1, x=0.99, y=0.01, xanchor="right",
        yanchor="bottom", bgcolor=PANEL, bordercolor=CIAN, borderwidth=1,
        font=dict(color=CIAN, size=12), pad=dict(l=6, r=6, t=3, b=3),
        buttons=[dict(label="Decimales", method="relayout", args=[con], args2=[sin])])])


def _rangos_2d(a, b, rango):
    """Rangos del plano xy: cubren la zona graficada y siempre incluyen el origen."""
    m = 0.1 * rango
    return ([min(a - rango, 0) - m, max(a + rango, 0) + m],
            [min(b - rango, 0) - m, max(b + rango, 0) + m])


def _ejes_2d(fig, xr, yr):
    """Ejes x/y neón con flechas y etiquetas detalladas (nombre + valor del extremo)."""
    fig.add_scatter(x=list(xr), y=[0, 0], mode="lines", line=dict(color=MAGENTA, width=3),
                    showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=[0, 0], y=list(yr), mode="lines", line=dict(color=LIMA, width=3),
                    showlegend=False, hoverinfo="skip")
    # (nombre, x, y, color, dirección dx, dy, desplazamiento de la etiqueta en píxeles)
    extremos = [("x", xr[1], 0, MAGENTA, 1, 0, (-50, 22)), ("-x", xr[0], 0, MAGENTA, -1, 0, (50, 22)),
                ("y", 0, yr[1], LIMA, 0, 1, (48, -22)), ("-y", 0, yr[0], LIMA, 0, -1, (48, 22))]
    for nombre, px, py, col, dx, dy, (sx, sy) in extremos:
        fig.add_annotation(x=px, y=py, ax=-28 * dx, ay=28 * dy, axref="pixel", ayref="pixel", text="",
                           showarrow=True, arrowhead=2, arrowsize=1.4, arrowwidth=2.5, arrowcolor=col)
        valor = px if dy == 0 else py
        fig.add_annotation(x=px, y=py, xshift=sx, yshift=sy, showarrow=False,
                           text=f"<b>{nombre}</b> <span style='font-size:12px'>({valor:+.1f})</span>",
                           font=dict(color=col, size=20))


def _ejes_3d(fig, L):
    """Ejes x/y/z neón con flechas, origen y etiquetas detalladas (nombre + valor del extremo)."""
    direcciones = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for (nombre, col), p in zip(ETIQUETAS[::2], direcciones[::2]):
        fig.add_scatter3d(x=[-L * p[0], L * p[0]], y=[-L * p[1], L * p[1]], z=[-L * p[2], L * p[2]],
                          mode="lines", line=dict(color=col, width=7), showlegend=False, hoverinfo="skip")
        fig.add_trace(go.Cone(x=[L * p[0]], y=[L * p[1]], z=[L * p[2]], u=[p[0]], v=[p[1]], w=[p[2]],
                              anchor="tip", sizemode="absolute", sizeref=L * 0.16, showscale=False,
                              colorscale=[[0, col], [1, col]], hoverinfo="skip"))
    fig.add_scatter3d(x=[0], y=[0], z=[0], mode="markers+text", text=["0"], textposition="bottom center",
                      marker=dict(size=4, color="white"), textfont=dict(color="white", size=14),
                      showlegend=False, hoverinfo="skip")
    d = 1.10 * L
    for (texto, col), p in zip(ETIQUETAS, direcciones):
        fig.add_scatter3d(x=[d * p[0]], y=[d * p[1]], z=[d * p[2]], mode="text",
                          text=[f"{texto} ({L * sum(p):+.1f})"], textfont=dict(color=col, size=20),
                          showlegend=False, hoverinfo="skip")
    _numeros_3d(fig, L)


# Mientras este valor no cambie, Plotly conserva el zoom, la rotación y el desplazamiento que haga el usuario
# aunque se pulsen los botones (Curvas de nivel, Decimales) o se vuelva a dibujar la gráfica.
UI_REVISION = "math2lab"
HOLGURA_CAJA = 1.6   # distancia de las paredes de la caja 3D respecto al modelo (1 = pegadas al borde de los ejes)


def _paso_numeros(L):
    """Separación entre los números de los ejes: siempre de 1 en 1. Solo con rangos descomunales (más de 60
    unidades por lado) se espacian, para no colgar el navegador con miles de etiquetas."""
    for p in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000):
        if L / p <= 60:
            return p
    return max(int(L // 60), 1)


def _alto_3d(L):
    """Altura de la gráfica 3D: crece con el rango para que los números de los ejes (de 1 en 1) se separen más."""
    return int(min(560 + 15 * max(L - 5, 0), 900))


def _numeros_3d(fig, L):
    """Números sobre los ejes x, y, z, cada uno con un círculo pequeño en su posición.
    Hay dos grupos de trazos: enteros (visibles) y decimales (ocultos hasta pulsar el botón «Decimales»)."""
    paso = _paso_numeros(L)
    tamano, circulo = (13, 5) if L <= 10 else (11, 5) if L <= 25 else (9, 4)
    posiciones = ["bottom center", "bottom center", "middle left"]
    for grupo, salto in (("ent", paso), ("dec", paso / 2 if L <= 4 else paso)):
        n = int(L // salto)
        valores = [k * salto for k in range(-n, n + 1) if k != 0]
        textos = [str(int(round(v))) if grupo == "ent" else f"{v:.1f}" for v in valores]
        ceros = [0] * len(valores)
        for (_, col), (px, py, pz), pos in zip(ETIQUETAS[::2],
                                               [(valores, ceros, ceros), (ceros, valores, ceros), (ceros, ceros, valores)],
                                               posiciones):
            fig.add_scatter3d(x=px, y=py, z=pz, mode="markers+text", text=textos, textposition=pos,
                              marker=dict(size=circulo, color=col, line=dict(color="white", width=1)),
                              textfont=dict(color=col, size=tamano, family="Arial, sans-serif"),
                              meta=grupo, visible=(grupo == "ent"), showlegend=False, hoverinfo="skip")


def _botones_3d(fig):
    """Botones en la esquina inferior derecha de la gráfica 3D (todos empiezan desactivados):
    «Curvas de nivel» (arriba, solo si la figura las tiene) y «Decimales» (abajo)."""
    indices = {g: [i for i, tr in enumerate(fig.data) if tr.meta == g] for g in ("ent", "dec", "curvas")}
    ent, dec, curvas = indices["ent"], indices["dec"], indices["curvas"]
    base = dict(type="buttons", direction="left", showactive=False, active=-1, x=0.99, xanchor="right",
                yanchor="bottom", bgcolor=PANEL, bordercolor=CIAN, borderwidth=1, font=dict(color=CIAN, size=12),
                pad=dict(l=6, r=6, t=3, b=3))
    menus = [dict(base, y=0.01, buttons=[dict(
        label="Decimales", method="restyle",
        args=[{"visible": [True] * len(dec) + [False] * len(ent)}, dec + ent],
        args2=[{"visible": [False] * len(dec) + [True] * len(ent)}, dec + ent])])]
    if curvas:
        menus.insert(0, dict(base, y=0.085, buttons=[dict(
            label="Curvas de nivel", method="restyle",
            args=[{"visible": True}, curvas], args2=[{"visible": False}, curvas])]))
    fig.update_layout(updatemenus=menus)


def _escena(L):
    """Caja 3D sin números en las paredes (los números van sobre los ejes, ver _numeros_3d)."""
    eje = dict(range=[-HOLGURA_CAJA * L, HOLGURA_CAJA * L], backgroundcolor=FONDO, gridcolor=GRILLA,
               showbackground=True, zeroline=False, showspikes=False, showticklabels=False, ticks="",
               title=dict(text=""), dtick=_paso_numeros(L), tick0=0)
    return dict(xaxis=eje, yaxis=eje, zaxis=eje, aspectmode="cube",
                camera=dict(eye=dict(x=1.6, y=-1.6, z=1.0)))


def _limpiar(Z):
    Z = np.array(Z, dtype=float)
    Z[~np.isfinite(Z)] = np.nan
    return Z


@lru_cache(maxsize=24)
def _malla(f, a, b, rango, n):
    """Malla (xs, ys, X, Y, Z) de f alrededor de (a, b). Se guarda en caché: no se recalcula si nada cambió."""
    xs, ys = np.linspace(a - rango, a + rango, n), np.linspace(b - rango, b + rango, n)
    X, Y = np.meshgrid(xs, ys)
    return xs, ys, X, Y, _limpiar(evaluar(f, X, Y))


BARRA_Z = dict(title=dict(text="z"), thickness=10, outlinewidth=0, tickfont=dict(color=TEXTO))


def _layout_2d(fig, xr, yr, **extra):
    """Estilo común de las gráficas 2D: fondo oscuro, ejes de 1 en 1 y botón de decimales."""
    fig.update_layout(
        paper_bgcolor=FONDO, plot_bgcolor=FONDO, font=dict(color=TEXTO), showlegend=False, uirevision=UI_REVISION,
        xaxis=dict(range=xr, gridcolor=GRILLA, zeroline=False, color=TEXTO, scaleanchor="y",
                   constrain="domain", **_ticks(xr)),
        yaxis=dict(range=yr, gridcolor=GRILLA, zeroline=False, color=TEXTO, constrain="domain",
                   **_ticks(yr, False)), **extra)
    _boton_decimales(fig, ["xaxis", "yaxis"])


# ------------------------------------------------------------------ gráficas
def figura_3d(f, a, b, rango, titulo=""):
    """Superficie 3D neón sobre fondo oscuro, con ejes x, -x, y, -y, z, -z."""
    _, _, X, Y, Z = _malla(f, a, b, rango, 90)
    Z = Z.copy()                                   # se modifica más abajo; no se debe tocar la caché
    if np.isfinite(Z).any():
        tope = max(np.nanpercentile(np.abs(Z), 98) * 1.5, 1e-6)
        Z[np.abs(Z) > tope] = np.nan
    fig = go.Figure()
    fig.add_surface(x=X, y=Y, z=Z, showscale=False, opacity=OPACIDAD_3D, colorscale=ESCALA_NEON,
                    lighting=dict(ambient=0.6, diffuse=0.8, specular=0.4))
    # Curvas de nivel f(x, y) = c: cada una sobre la superficie, a su altura z = c, y proyectada en la base de la caja
    zfin = Z[np.isfinite(Z)]
    if zfin.size and zfin.max() - zfin.min() > 1e-9:
        zmin, zmax = float(zfin.min()), float(zfin.max())
        fig.add_surface(x=X, y=Y, z=Z, hidesurface=True, showscale=False, visible=False, meta="curvas",
                        hoverinfo="skip", colorscale=[[0, CELESTE_NEON], [1, CELESTE_NEON]],
                        contours=dict(z=dict(show=True, usecolormap=False, color=CELESTE_NEON, width=5,
                                             start=zmin, end=zmax, size=(zmax - zmin) / 14,
                                             project=dict(z=True))))
    zm = float(np.nanmax(np.abs(Z))) if np.isfinite(Z).any() else rango
    L = max(rango + max(abs(a), abs(b)), zm)
    _ejes_3d(fig, L)
    v = evaluar(f, np.array([float(a)]), np.array([float(b)]))[0]
    if np.isfinite(v):
        fig.add_scatter3d(x=[a], y=[b], z=[v], mode="markers", name="Punto (a, b)",
                          marker=dict(size=7, color=LIMA, line=dict(color="white", width=1)))
    fig.update_layout(title=titulo, height=_alto_3d(L), paper_bgcolor=FONDO, font=dict(color=TEXTO),
                      margin=dict(l=0, r=0, t=40, b=0), scene=_escena(L), uirevision=UI_REVISION,
                      legend=dict(x=0, y=1, font=dict(color=TEXTO)))
    _botones_3d(fig)
    return fig


def figura_2d(f, a, b, rango, n=18):
    """Vista 2D (plano xy): mapa de alturas de f con ejes x, -x, y, -y y el punto (a, b)."""
    xs, ys, _, _, Z = _malla(f, a, b, rango, 200)
    zmin = zmax = None
    if np.isfinite(Z).any():
        zmin, zmax = float(np.nanpercentile(Z, 2)), float(np.nanpercentile(Z, 98))
        if zmax - zmin < 1e-9:
            zmin, zmax = zmin - 1, zmax + 1
    xr, yr = _rangos_2d(a, b, rango)
    fig = go.Figure(go.Contour(x=xs, y=ys, z=Z, ncontours=n, colorscale=ESCALA_NEON, zmin=zmin, zmax=zmax,
                               contours=dict(coloring="fill", showlines=True),
                               line=dict(color="rgba(255,255,255,0.22)", width=1), colorbar=BARRA_Z))
    _ejes_2d(fig, xr, yr)
    fig.add_scatter(x=[a], y=[b], mode="markers", name="Punto (a, b)",
                    marker=dict(size=11, color=LIMA, symbol="diamond", line=dict(color="white", width=1)))
    _layout_2d(fig, xr, yr, title="Vista 2D · plano xy", height=560, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def figura_curvas(f, a, b, rango, n, c=None):
    xs, ys, _, _, Z = _malla(f, a, b, rango, 200)
    cont = dict(coloring="lines", showlabels=True, labelfont=dict(color=TEXTO, size=11))
    if c is not None:
        cont.update(start=c, end=c, size=1)
    xr, yr = _rangos_2d(a, b, rango)
    fig = go.Figure(go.Contour(x=xs, y=ys, z=Z, ncontours=n, contours=cont, line=dict(width=2.5),
                               colorscale=ESCALA_LINEAS, colorbar=BARRA_Z))
    _ejes_2d(fig, xr, yr)
    _layout_2d(fig, xr, yr, height=600, margin=dict(l=20, r=20, t=30, b=20))
    return fig


def figura_nivel_3d(w, c_min, c_max, n, rango):
    g = np.linspace(-rango, rango, 40)
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    V = _limpiar(evaluar(w, X, Y, Z))
    fig = go.Figure(go.Isosurface(x=X.flatten(), y=Y.flatten(), z=Z.flatten(), value=V.flatten(),
                                  isomin=c_min, isomax=c_max if n > 1 else c_min, surface_count=n,
                                  caps=dict(x_show=False, y_show=False, z_show=False),
                                  colorscale=ESCALA_LINEAS, opacity=0.55, showscale=True,
                                  colorbar=dict(thickness=10, outlinewidth=0, tickfont=dict(color=TEXTO))))
    _ejes_3d(fig, rango)
    fig.update_layout(height=620, paper_bgcolor=FONDO, font=dict(color=TEXTO),
                      margin=dict(l=0, r=0, t=20, b=0), showlegend=False, scene=_escena(rango),
                      uirevision=UI_REVISION)
    _botones_3d(fig)
    return fig


USAR_VISOR_PROPIO = True   # False = usar el gráfico estándar de Streamlit (su pantalla completa reinicia el zoom)


def mostrar(fig):
    """Muestra una figura de Plotly. Con el visor propio, la pantalla completa conserva el zoom del usuario."""
    if USAR_VISOR_PROPIO:
        try:
            visor_plotly(fig, int(fig.layout.height or 560))
            return
        except Exception:
            pass                              # si algo falla, se usa el gráfico estándar de Streamlit
    try:
        st.plotly_chart(fig, use_container_width=True)
    except TypeError:
        st.plotly_chart(fig, width="stretch")


def _dibujar(constructor, *args):
    """Dibuja una gráfica; si falla, muestra el error exacto en pantalla en vez de dejarla en blanco."""
    try:
        mostrar(constructor(*args))
    except Exception as e:
        st.error(f"No se pudo dibujar ({constructor.__name__}): {type(e).__name__}: {e}")


def graficas_duales(f, a, b, rango, titulo="Vista 3D · z = f(x, y)"):
    """Muestra el mismo ejercicio en dos gráficas: 2D (izquierda) y 3D (derecha)."""
    c1, c2 = st.columns(2 if rango <= 8 else [1, 2])      # con rangos grandes, más ancho para la 3D
    with c1:
        _dibujar(figura_2d, f, a, b, rango)
    with c2:
        _dibujar(figura_3d, f, a, b, rango, titulo)