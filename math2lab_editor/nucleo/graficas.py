from functools import lru_cache

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from nucleo.matematica import evaluar
from nucleo.tema import (
    CELESTE_NEON, CIAN, ESCALA_LINEAS, ESCALA_NEON, ETIQUETAS, FONDO, GRILLA, LIMA, MAGENTA, OPACIDAD_3D, PANEL,
    TEXTO)
from nucleo.visor import visor_plotly

UI_REVISION = "math2lab"
HOLGURA_CAJA = 1.6
USAR_VISOR_PROPIO = True
BARRA_Z = dict(title=dict(text="z"), thickness=10, outlinewidth=0, tickfont=dict(color=TEXTO))
MENU_BASE = dict(type="buttons", direction="left", showactive=False, active=-1, x=0.99, xanchor="right",
                 yanchor="bottom", bgcolor=PANEL, bordercolor=CIAN, borderwidth=1, font=dict(color=CIAN, size=12),
                 pad=dict(l=6, r=6, t=3, b=3))
PASOS_NUMEROS = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000)


def _ticks(r, eje_x=True):
    span = abs(r[1] - r[0])
    return dict(dtick=1, tick0=0, tickformat="d", tickfont=dict(size=12 if span <= 20 else 9),
                tickangle=-90 if (eje_x and span > 20) else 0)


def _boton_decimales(fig, ejes):
    con, sin = {}, {}
    for e in ejes:
        con.update({f"{e}.dtick": 0.5, f"{e}.tickformat": ".1f"})
        sin.update({f"{e}.dtick": 1, f"{e}.tickformat": "d"})
    boton = dict(label="Decimales", method="relayout", args=[con], args2=[sin])
    fig.update_layout(updatemenus=[dict(MENU_BASE, y=0.01, buttons=[boton])])


def _rangos_2d(a, b, rango):
    m = 0.1 * rango
    return ([min(a - rango, 0) - m, max(a + rango, 0) + m],
            [min(b - rango, 0) - m, max(b + rango, 0) + m])


def _ejes_2d(fig, xr, yr):
    for xs, ys, color in ((list(xr), [0, 0], MAGENTA), ([0, 0], list(yr), LIMA)):
        fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=3), showlegend=False, hoverinfo="skip")
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
    direcciones = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for (_, col), p in zip(ETIQUETAS[::2], direcciones[::2]):
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


def _paso_numeros(L):
    for p in PASOS_NUMEROS:
        if L / p <= 60:
            return p
    return max(int(L // 60), 1)


def _alto_3d(L):
    return int(min(560 + 15 * max(L - 5, 0), 900))


def _numeros_3d(fig, L):
    paso = _paso_numeros(L)
    tamano, circulo = (13, 5) if L <= 10 else (11, 5) if L <= 25 else (9, 4)
    posiciones = ["bottom center", "bottom center", "middle left"]
    for grupo, salto in (("ent", paso), ("dec", paso / 2 if L <= 4 else paso)):
        n = int(L // salto)
        valores = [k * salto for k in range(-n, n + 1) if k != 0]
        textos = [str(int(round(v))) if grupo == "ent" else f"{v:.1f}" for v in valores]
        ceros = [0] * len(valores)
        coordenadas = [(valores, ceros, ceros), (ceros, valores, ceros), (ceros, ceros, valores)]
        for (_, col), (px, py, pz), pos in zip(ETIQUETAS[::2], coordenadas, posiciones):
            fig.add_scatter3d(x=px, y=py, z=pz, mode="markers+text", text=textos, textposition=pos,
                              marker=dict(size=circulo, color=col, line=dict(color="white", width=1)),
                              textfont=dict(color=col, size=tamano, family="Arial, sans-serif"),
                              meta=grupo, visible=(grupo == "ent"), showlegend=False, hoverinfo="skip")


def _botones_3d(fig):
    indices = {g: [i for i, tr in enumerate(fig.data) if tr.meta == g] for g in ("ent", "dec", "curvas")}
    ent, dec, curvas = indices["ent"], indices["dec"], indices["curvas"]
    decimales = dict(label="Decimales", method="restyle",
                     args=[{"visible": [True] * len(dec) + [False] * len(ent)}, dec + ent],
                     args2=[{"visible": [False] * len(dec) + [True] * len(ent)}, dec + ent])
    menus = [dict(MENU_BASE, y=0.01, buttons=[decimales])]
    if curvas:
        niveles = dict(label="Curvas de nivel", method="restyle",
                       args=[{"visible": True}, curvas], args2=[{"visible": False}, curvas])
        menus.insert(0, dict(MENU_BASE, y=0.085, buttons=[niveles]))
    fig.update_layout(updatemenus=menus)


def _escena(L):
    eje = dict(range=[-HOLGURA_CAJA * L, HOLGURA_CAJA * L], backgroundcolor=FONDO, gridcolor=GRILLA,
               showbackground=True, zeroline=False, showspikes=False, showticklabels=False, ticks="",
               title=dict(text=""), dtick=_paso_numeros(L), tick0=0)
    return dict(xaxis=eje, yaxis=eje, zaxis=eje, aspectmode="cube", camera=dict(eye=dict(x=1.6, y=-1.6, z=1.0)))


def _layout_3d(fig, L, **extra):
    fig.update_layout(paper_bgcolor=FONDO, font=dict(color=TEXTO), scene=_escena(L), uirevision=UI_REVISION, **extra)
    _botones_3d(fig)


def _layout_2d(fig, xr, yr, **extra):
    fig.update_layout(
        paper_bgcolor=FONDO, plot_bgcolor=FONDO, font=dict(color=TEXTO), showlegend=False, uirevision=UI_REVISION,
        xaxis=dict(range=xr, gridcolor=GRILLA, zeroline=False, color=TEXTO, scaleanchor="y",
                   constrain="domain", **_ticks(xr)),
        yaxis=dict(range=yr, gridcolor=GRILLA, zeroline=False, color=TEXTO, constrain="domain",
                   **_ticks(yr, False)), **extra)
    _boton_decimales(fig, ["xaxis", "yaxis"])


def _limpiar(Z):
    Z = np.array(Z, dtype=float)
    Z[~np.isfinite(Z)] = np.nan
    return Z


@lru_cache(maxsize=24)
def _malla(f, a, b, rango, n):
    xs, ys = np.linspace(a - rango, a + rango, n), np.linspace(b - rango, b + rango, n)
    X, Y = np.meshgrid(xs, ys)
    return xs, ys, X, Y, _limpiar(evaluar(f, X, Y))


def figura_3d(f, a, b, rango, titulo=""):
    _, _, X, Y, Z = _malla(f, a, b, rango, 90)
    Z = Z.copy()
    if np.isfinite(Z).any():
        tope = max(np.nanpercentile(np.abs(Z), 98) * 1.5, 1e-6)
        Z[np.abs(Z) > tope] = np.nan
    fig = go.Figure()
    fig.add_surface(x=X, y=Y, z=Z, showscale=False, opacity=OPACIDAD_3D, colorscale=ESCALA_NEON,
                    lighting=dict(ambient=0.6, diffuse=0.8, specular=0.4))
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
    _layout_3d(fig, L, title=titulo, height=_alto_3d(L), margin=dict(l=0, r=0, t=40, b=0),
               legend=dict(x=0, y=1, font=dict(color=TEXTO)))
    return fig


def figura_2d(f, a, b, rango, n=18):
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
    _layout_3d(fig, rango, height=620, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    return fig


def mostrar(fig):
    if USAR_VISOR_PROPIO:
        try:
            visor_plotly(fig, int(fig.layout.height or 560))
            return
        except Exception:
            pass
    try:
        st.plotly_chart(fig, use_container_width=True)
    except TypeError:
        st.plotly_chart(fig, width="stretch")


def _dibujar(constructor, *args):
    try:
        mostrar(constructor(*args))
    except Exception as e:
        st.error(f"No se pudo dibujar ({constructor.__name__}): {type(e).__name__}: {e}")


def graficas_duales(f, a, b, rango, titulo="Vista 3D · z = f(x, y)"):
    c1, c2 = st.columns(2 if rango <= 8 else [1, 2])
    with c1:
        _dibujar(figura_2d, f, a, b, rango)
    with c2:
        _dibujar(figura_3d, f, a, b, rango, titulo)
