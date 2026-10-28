"""Identidad de la plataforma: nombre, logotipo (zorro sobre una silla de montar) e icono de la pestaña."""
import base64
from functools import lru_cache
from pathlib import Path

NOMBRE = "FoxSaddle"
_ASSETS = Path(__file__).resolve().parent.parent / "assets"      # carpeta assets/ junto a app.py

# Brillo neón celeste. Se escribe como estilo en línea (no en una hoja de estilos) para que se aplique siempre
BRILLO_LOGO = "drop-shadow(0 0 3px #4AF7F3) drop-shadow(0 0 10px rgba(0,245,255,.30)) drop-shadow(0 0 22px rgba(0,245,255,.55))"
BRILLO_TEXTO = "0 0 4px #00f5ff, 0 0 12px rgba(0,245,255,.9), 0 0 26px rgba(0,245,255,.6)"


def ruta_icono():
    """Imagen cuadrada para la pestaña del navegador (favicon)."""
    return _ASSETS / "foxsaddle_icono.png"


@lru_cache(maxsize=1)
def logo_html():
    """Logotipo + nombre (uno al lado del otro) para la barra lateral. La imagen va incrustada (base64) para no
    depender de rutas. Todo el estilo va EN LÍNEA: así el diseño y el brillo no dependen de otra hoja de estilos.
    El nombre es un <h1> sin fuente propia: usa la MISMA tipografía de los títulos de la página (la que tenía
    el nombre antes del cambio), con su peso fino (300), su espaciado de 2 px y el brillo celeste."""
    datos = base64.b64encode((_ASSETS / "foxsaddle_logo.png").read_bytes()).decode()
    # Contenedor con "container-type": las unidades cqw miden el ancho de la propia barra lateral. En su ancho normal
    # el resultado es el de siempre (los mínimos de clamp); al ensanchar la barra, el logo y el nombre crecen con ella.
    # Cada tamaño lleva primero un valor fijo: los navegadores sin cqw usan ese.
    return (f'<div style="container-type:inline-size;width:100%;">'
            f'<div style="display:flex;align-items:center;gap:12px;flex-wrap:nowrap;margin:0 0 .6rem 0;">'
            f'<img alt="{NOMBRE}" src="data:image/png;base64,{datos}" '
            f'style="width:140px;width:clamp(140px,42cqw,240px);height:auto;flex:none;filter:{BRILLO_LOGO};">'
            f'<h1 style="margin:0;padding:0;font-size:1.9rem;font-size:clamp(1.9rem,7.5cqw,3.6rem);font-weight:300;'
            f'letter-spacing:2px;line-height:1.1;color:#00f5ff;text-shadow:{BRILLO_TEXTO};white-space:nowrap;">'
            f'{NOMBRE}</h1></div></div>')