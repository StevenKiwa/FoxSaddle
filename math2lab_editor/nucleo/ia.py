"""Conexión con la IA (Gemini): clave, modelos de respaldo, streaming y cupo de preguntas por sesión."""
import os
import time
from pathlib import Path

import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------------ IA (Gemini)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODELO_DEFECTO = "gemini-flash-latest"   # alias del modelo Flash vigente; se puede cambiar en secrets (GEMINI_MODEL)
SISTEMA = ("Eres un tutor de Matemática II (límites y derivadas parciales de funciones de varias variables). "
           "Explica en español, de forma amplia y paso a paso: primero la idea general, luego cada paso con su "
           "justificación, y al final un resumen y un error común. Usa LaTeX entre $...$. "
           "Si te dan resultados calculados por el sistema, úsalos y no los contradigas. "
           "Si no estás seguro de un paso, dilo con claridad.")


def _secreto(nombre, defecto=""):
    try:
        return st.secrets.get(nombre, defecto)
    except Exception:
        return defecto


def clave_gemini():
    """Clave de Gemini (solo la ve el programador): secrets.toml, variable de entorno o clave_gemini.txt."""
    for c in (str(_secreto("GEMINI_API_KEY")), os.environ.get("GEMINI_API_KEY", "")):
        if c.strip() and c.strip() != "PEGA_AQUI_TU_CLAVE":
            return c.strip()
    archivo = Path(__file__).resolve().parent.parent / "clave_gemini.txt"
    if archivo.exists():
        c = archivo.read_text(encoding="utf-8").strip().strip('"').strip("'")
        if c and c != "PEGA_AQUI_TU_CLAVE":
            return c
    return ""


MAX_PREGUNTAS_IA = 30   # por sesión de usuario; se puede cambiar con LIMITE_IA en secrets.toml


def cupo_ia():
    """Protege la cuota gratuita de la clave compartida: cada sesión tiene un máximo de preguntas a la IA."""
    usadas = st.session_state.get("ia_usadas", 0)
    if usadas >= int(_secreto("LIMITE_IA", MAX_PREGUNTAS_IA)):
        return False
    st.session_state.ia_usadas = usadas + 1
    return True


MSG_LIMITE = "Alcanzaste el límite de preguntas a la IA de esta sesión. Recarga la página más tarde para continuar."


def mensaje_error(e):
    txt = str(e)
    if "503" in txt or "UNAVAILABLE" in txt:
        return ("Gemini está saturado en este momento (error 503). Ya probé con varios modelos sin éxito: "
                "intenta de nuevo en uno o dos minutos.")
    if "429" in txt:
        return "Se alcanzó el límite gratuito de Gemini. Espera un minuto e inténtalo de nuevo."
    if any(c in txt for c in ("401", "403", "404", "API key")):
        return "La IA no está disponible por el momento. Inténtalo más tarde."
    if "imeout" in txt or "timed out" in txt:
        return "Gemini tardó demasiado en responder. Inténtalo de nuevo."
    return "No se pudo obtener la respuesta de la IA. Inténtalo de nuevo en un momento."


# Si un modelo está saturado, se prueba el siguiente automáticamente.
MODELOS_RESPALDO = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash"]


def _modelos():
    principal = str(_secreto("GEMINI_MODEL", "")).strip()
    return list(dict.fromkeys(([principal] if principal else []) + MODELOS_RESPALDO))


def _transitorio(e):
    txt = str(e)
    return any(c in txt for c in ("503", "429", "500", "UNAVAILABLE", "imeout", "timed out"))


def _cliente():
    # sin reintentos internos (los hacemos nosotros, más rápido) y con tiempo máximo de espera
    return OpenAI(base_url=GEMINI_URL, api_key=clave_gemini(), max_retries=0, timeout=40)


def flujo_ia(mensajes):
    """Genera la respuesta por trozos (streaming), con reintento y cambio de modelo si hay saturación."""
    ultimo = None
    for modelo in _modelos():
        for intento in range(2):
            emitido = False
            try:
                flujo = _cliente().chat.completions.create(
                    model=modelo, stream=True,
                    messages=[{"role": "system", "content": SISTEMA}] + mensajes[-12:])
                for trozo in flujo:
                    if trozo.choices and trozo.choices[0].delta.content:
                        emitido = True
                        yield trozo.choices[0].delta.content
                return
            except Exception as e:
                ultimo = e
                if emitido or not _transitorio(e):
                    raise
                if intento == 0:
                    time.sleep(2)
    raise ultimo


def pedir_ia(contexto):
    if not clave_gemini():
        return "⚠️ La IA no está disponible por el momento. Inténtalo más tarde."
    if not cupo_ia():
        return MSG_LIMITE
    try:
        return "".join(flujo_ia([{"role": "user", "content": contexto}]))
    except Exception as e:
        return mensaje_error(e)


def bloque_ia(contexto, clave):
    if st.button(" Explicar paso a paso con IA", key=clave):
        with st.spinner("La IA está preparando la explicación..."):
            st.markdown(pedir_ia(contexto))
