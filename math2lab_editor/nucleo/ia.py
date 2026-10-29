import json
import os
import time
from pathlib import Path

import requests
import streamlit as st

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"
MODELOS_RESPALDO = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash"]
MAX_PREGUNTAS_IA = 30
MSG_LIMITE = "Alcanzaste el límite de preguntas a la IA de esta sesión. Recarga la página más tarde para continuar."
MSG_NO_DISPONIBLE = "La IA no está disponible por el momento. Inténtalo más tarde."
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


def _clave_valida(clave):
    clave = clave.strip()
    return clave if clave and clave != "PEGA_AQUI_TU_CLAVE" else ""


def clave_gemini():
    for origen in (str(_secreto("GEMINI_API_KEY")), os.environ.get("GEMINI_API_KEY", "")):
        if _clave_valida(origen):
            return origen.strip()
    archivo = Path(__file__).resolve().parent.parent / "clave_gemini.txt"
    if archivo.exists():
        return _clave_valida(archivo.read_text(encoding="utf-8").strip().strip('"').strip("'"))
    return ""


def cupo_ia():
    usadas = st.session_state.get("ia_usadas", 0)
    if usadas >= int(_secreto("LIMITE_IA", MAX_PREGUNTAS_IA)):
        return False
    st.session_state.ia_usadas = usadas + 1
    return True


def _contiene(texto, marcas):
    return any(m in texto for m in marcas)


def mensaje_error(e):
    txt = str(e)
    if _contiene(txt, ("503", "UNAVAILABLE")):
        return ("Gemini está saturado en este momento (error 503). Ya probé con varios modelos sin éxito: "
                "intenta de nuevo en uno o dos minutos.")
    if "429" in txt:
        return "Se alcanzó el límite gratuito de Gemini. Espera un minuto e inténtalo de nuevo."
    if _contiene(txt, ("401", "403", "404", "API key")):
        return MSG_NO_DISPONIBLE
    if _contiene(txt, ("imeout", "timed out")):
        return "Gemini tardó demasiado en responder. Inténtalo de nuevo."
    return "No se pudo obtener la respuesta de la IA. Inténtalo de nuevo en un momento."


def _modelos():
    principal = str(_secreto("GEMINI_MODEL", "")).strip()
    return list(dict.fromkeys(([principal] if principal else []) + MODELOS_RESPALDO))


def _transitorio(e):
    return _contiene(str(e), ("503", "429", "500", "UNAVAILABLE", "imeout", "timed out"))


def _contenidos(mensajes):
    return [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
            for m in mensajes]


def _textos(linea):
    if not linea.startswith(b"data:"):
        return
    try:
        trozo = json.loads(linea[5:].decode("utf-8"))
    except ValueError:
        return
    for candidato in trozo.get("candidates", []):
        for parte in (candidato.get("content") or {}).get("parts", []):
            if parte.get("text") and not parte.get("thought"):
                yield parte["text"]


def _flujo_modelo(modelo, mensajes):
    url = f"{GEMINI_URL}/models/{modelo}:streamGenerateContent"
    cuerpo = {"systemInstruction": {"parts": [{"text": SISTEMA}]}, "contents": _contenidos(mensajes)}
    hubo_texto = False
    with requests.post(url, params={"alt": "sse"}, json=cuerpo, stream=True, timeout=(10, 40),
                       headers={"x-goog-api-key": clave_gemini()}) as r:
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
        for linea in r.iter_lines():
            for texto in _textos(linea):
                hubo_texto = True
                yield texto
    if not hubo_texto:
        raise RuntimeError("HTTP 200: la IA devolvió una respuesta vacía")


def flujo_ia(mensajes):
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
                print(f"[IA] modelo={modelo} intento={intento + 1}: {str(e)[:300]}", flush=True)
                if emitido or not _transitorio(e):
                    raise
                if intento == 0:
                    time.sleep(2)
    raise ultimo


def pedir_ia(contexto):
    if not clave_gemini():
        return "⚠️ " + MSG_NO_DISPONIBLE
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
