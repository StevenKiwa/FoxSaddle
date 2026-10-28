"""Editor visual de fórmulas (MathLive) como componente de Streamlit.

El editor está en nucleo/editor_frontend/index.html. Devuelve {"latex": ..., "n": ...} cada vez que el
usuario pulsa Enter o «Aplicar»; si no ha aplicado nada todavía, devuelve None.
"""
from pathlib import Path

import streamlit.components.v1 as components

_componente = components.declare_component(
    "math2lab_editor", path=str(Path(__file__).resolve().parent / "editor_frontend"))


def editor_formula(latex, version, key="editor_formula"):
    """Muestra el editor con `latex` como contenido.
    `version`: súbela en 1 cuando cambies la fórmula desde fuera (por ejemplo al escribirla como texto)."""
    return _componente(latex=latex, version=version, key=key, default=None)
