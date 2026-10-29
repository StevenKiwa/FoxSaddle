import base64
from functools import lru_cache
from pathlib import Path

NOMBRE = "FoxSaddle"
_ASSETS = Path(__file__).resolve().parent.parent / "assets"

BRILLO_LOGO = "drop-shadow(0 0 3px #4AF7F3) drop-shadow(0 0 10px rgba(0,245,255,.30)) drop-shadow(0 0 22px rgba(0,245,255,.55))"
BRILLO_TEXTO = "0 0 4px #00f5ff, 0 0 12px rgba(0,245,255,.9), 0 0 26px rgba(0,245,255,.6)"


def ruta_icono():
    return _ASSETS / "foxsaddle_icono.png"


@lru_cache(maxsize=1)
def logo_html():
    datos = base64.b64encode((_ASSETS / "foxsaddle_logo.png").read_bytes()).decode()
    return (f'<div style="display:flex;align-items:center;gap:12px;flex-wrap:nowrap;margin:0 0 .6rem 0;">'
            f'<img alt="{NOMBRE}" src="data:image/png;base64,{datos}" '
            f'style="width:140px;height:auto;flex:none;filter:{BRILLO_LOGO};">'
            f'<h1 style="margin:0;padding:0;font-size:1.9rem;font-weight:300;letter-spacing:2px;line-height:1.1;'
            f'color:#00f5ff;text-shadow:{BRILLO_TEXTO};white-space:nowrap;">{NOMBRE}</h1></div>')
