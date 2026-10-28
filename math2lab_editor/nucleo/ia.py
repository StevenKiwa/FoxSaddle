"""Conexión con la IA (Gemini): clave, modelos de respaldo, streaming y cupo de preguntas por sesión.

Usa la API nativa de Gemini (no la compatible con OpenAI): así funcionan tanto las claves antiguas (AIza...)
como las nuevas (AQ....) de Google AI Studio, con las que la ruta compatible con OpenAI da errores.
"""
import json
import os
import time
from pathlib import Path

import requests
import streamlit as st

# ------------------------------------------------------------------ IA (Gemini)
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"
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


def _contenidos(mensajes):
    """Convierte el historial {role, content} al formato nativo de Gemini (user / model)."""
    return [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in mensajes]


def _flujo_modelo(modelo, mensajes):
    """Respuesta por trozos desde la API nativa de Gemini; la clave viaja en la cabecera x-goog-api-key."""
    url = f"{GEMINI_URL}/models/{modelo}:streamGenerateContent"
    cuerpo = {"systemInstruction": {"parts": [{"text": SISTEMA}]}, "contents": _contenidos(mensajes)}
    with requests.post(url, params={"alt": "sse"}, json=cuerpo, stream=True, timeout=(10, 40),
                       headers={"x-goog-api-key": clave_gemini()}) as r:
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        hubo_texto = False
        for linea in r.iter_lines():
            if not linea.startswith(b"data:"):
                continue
            dato = linea[5:].strip()
            if not dato:
                continue
            try:
                trozo = json.loads(dato.decode("utf-8"))
            except ValueError:
                continue
            for cand in trozo.get("candidates", []):
                for parte in (cand.get("content") or {}).get("parts", []):
                    if parte.get("text") and not parte.get("thought"):
                        hubo_texto = True
                        yield parte["text"]
        if not hubo_texto:
            raise RuntimeError("HTTP 200: la IA devolvió una respuesta vacía")


def flujo_ia(mensajes):
    """Genera la respuesta por trozos (streaming), con reintento y cambio de modelo si hay saturación."""
    ultimo = None
    for modelo in _modelos():
        for intento in range(2):
            emitido = False
            try:
                for texto in _flujo_modelo(modelo, mensajes[-12:]):
                    emitido = True
                    yield texto
                return
            except Exception as e:
                ultimo = e
                # Queda en los registros de la app (solo los ve quien administra el repositorio); nunca incluye la clave.
                print(f"[IA] modelo={modelo} intento={intento + 1}: {str(e)[:300]}", flush=True)
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
