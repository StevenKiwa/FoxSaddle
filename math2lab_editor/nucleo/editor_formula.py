from pathlib import Path

import streamlit.components.v1 as components

_componente = components.declare_component(
    "math2lab_editor", path=str(Path(__file__).resolve().parent / "editor_frontend"))


def editor_formula(latex, version, key="editor_formula"):
    return _componente(latex=latex, version=version, key=key, default=None)
