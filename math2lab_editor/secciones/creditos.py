import base64
from functools import lru_cache
from html import escape
from pathlib import Path

import streamlit as st

from nucleo.marca import NOMBRE
from nucleo.tema import CIAN, TEXTO

ASSETS = Path(__file__).resolve().parent.parent / "assets"
DOCENTE = "David Alexander T. Chávez"
INTEGRANTES = ["Steven Noel Montiel Hidalgo", "Daniel Isaías Corazon Trejos", "Medardo Antonio García Suazo", "Ferenc Andrés Hernández Ríos"]
CARRERA = "Ingeniería en computación"
UNIVERSIDAD = "UNI"
ANCHO_LOGO = 200
BRILLO = "0 0 4px #00f5ff, 0 0 12px rgba(0,245,255,.9), 0 0 26px rgba(0,245,255,.6)"


@lru_cache(maxsize=4)
def _imagen(archivo):
    return base64.b64encode((ASSETS / archivo).read_bytes()).decode()


def _marco(archivo, descripcion):
    return (f'<div style="flex:0 1 {ANCHO_LOGO}px;max-width:46%;box-sizing:border-box;padding:12px;'
            f'display:flex;align-items:center;justify-content:center;border:1px solid {CIAN};'
            f'border-radius:12px;box-shadow:0 0 14px rgba(0,245,255,.45);">'
            f'<img alt="{escape(descripcion)}" src="data:image/png;base64,{_imagen(archivo)}" '
            f'style="width:100%;height:auto;display:block;"></div>')


def _nombres():
    celdas = "".join(f'<span style="font-size:1.15rem;">{escape(n)}</span>' for n in INTEGRANTES)
    return f'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px 32px;margin-top:10px;">{celdas}</div>'


def creditos(ctx):
    st.markdown(
        f'<div style="text-align:center;max-width:760px;margin:0 auto;color:{TEXTO};line-height:1.6;">'
        f'<p style="margin:0;font-size:1.05rem;">Proyecto supervisado por</p>'
        f'<p style="margin:2px 0 28px 0;font-size:1.5rem;color:{CIAN};text-shadow:{BRILLO};">{escape(DOCENTE)}</p>'
        f'<p style="margin:0;font-size:1.05rem;">{escape(NOMBRE)}, página web para resolver funciones de límites '
        f'y derivadas, creada por</p>{_nombres()}'
        f'<p style="margin:28px 0 0 0;font-size:1.05rem;">Estudiantes de la carrera {escape(CARRERA)} '
        f'de la universidad {escape(UNIVERSIDAD)}</p>'
        f'<div style="display:flex;justify-content:center;align-items:stretch;gap:24px;margin-top:32px;">'
        f'{_marco("foxsaddle_logo.png", NOMBRE)}{_marco("logo_uni.png", "Logo de la UNI")}</div></div>',
        unsafe_allow_html=True)
