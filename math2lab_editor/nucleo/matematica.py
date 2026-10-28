"""Núcleo matemático: lectura segura de funciones, evaluación numérica y cálculos simbólicos (con caché)."""
import re
from functools import lru_cache

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr, standard_transformations)

x, y, z, s, t = sp.symbols("x y z s t", real=True)
r = sp.Symbol("r", positive=True)   # radio polar ρ > 0: así sqrt(r²) = r
TRANSF = standard_transformations + (implicit_multiplication_application, convert_xor)
LOCAL = {"x": x, "y": y, "z": z, "sen": sp.sin, "tan": sp.tan, "raiz": sp.sqrt, "ln": sp.log, "abs": sp.Abs}

# Nombres que el usuario puede escribir en una función (todo lo demás se rechaza).
NOMBRES_OK = {"x", "y", "z", "sen", "sin", "cos", "tan", "cot", "sec", "csc", "asin", "acos", "atan",
              "sinh", "cosh", "tanh", "exp", "ln", "log", "raiz", "sqrt", "abs", "Abs", "pi", "E"}
_GLOBAL = {}
exec("from sympy import *", _GLOBAL)       # espacio de nombres de SymPy...
_GLOBAL["__builtins__"] = {}               # ...sin acceso a las funciones internas de Python


def _validar(texto):
    """Seguridad: la página es pública, así que solo se aceptan expresiones matemáticas simples."""
    if len(texto) > 200:
        raise ValueError("La expresión es demasiado larga (máximo 200 caracteres).")
    if re.search(r"[^0-9A-Za-z_+\-*/^().,\s]", texto) or re.search(r"(?<!\d)\.|\.(?!\d)", texto):
        raise ValueError("Hay caracteres no permitidos. Usa números, x, y, z, + - * / ^ y paréntesis.")
    if re.search(r"\d{7,}", texto) or len(re.findall(r"\^|\*\*", texto)) > 6:
        raise ValueError("Números o potencias demasiado grandes.")
    for nombre in re.findall(r"[A-Za-z_]\w*", texto):
        if nombre not in NOMBRES_OK and not re.fullmatch(r"[xyz]+", nombre):
            raise ValueError(f"No se permite «{nombre}». Usa x, y, z y funciones como sen, cos, tan, raiz, ln, exp.")


def _revisar_potencias(expr):
    """Evita potencias numéricas gigantes (como 9^9^9) que dejarían la página colgada."""
    for p in sp.preorder_traversal(expr):
        if p.is_Pow and not p.free_symbols and not p.exp.free_symbols:
            if any(n.is_Pow and n.exp != -1 for n in sp.preorder_traversal(p.exp)) or abs(float(p.exp)) > 12:
                raise ValueError("Potencia numérica demasiado grande.")


@lru_cache(maxsize=256)
def leer(texto):
    """Convierte texto como 'x^2*y/(x^2+y^2)' en una expresión de SymPy (validada y con caché)."""
    _validar(texto)
    args = dict(transformations=TRANSF)
    _revisar_potencias(parse_expr(texto, local_dict=dict(LOCAL), global_dict=dict(_GLOBAL), evaluate=False, **args))
    return parse_expr(texto, local_dict=dict(LOCAL), global_dict=dict(_GLOBAL), **args)


@lru_cache(maxsize=64)
def _compilar(f, n):
    return sp.lambdify((x, y, z)[:n], f, "numpy")


def evaluar(f, *args):
    """Evalúa una expresión simbólica sobre arreglos de NumPy."""
    with np.errstate(all="ignore"):
        res = np.array(_compilar(f, len(args))(*args), dtype=float)
    return res * np.ones_like(args[0])


# ---- cálculos simbólicos con caché: no se repiten al mover un control o cambiar de paso del tutorial
@lru_cache(maxsize=64)
def limite_polar(f, a_s, b_s):
    g = sp.simplify(f.subs({x: a_s + r * sp.cos(t), y: b_s + r * sp.sin(t)}, simultaneous=True))
    return g, sp.simplify(sp.limit(g, r, 0, "+"))


@lru_cache(maxsize=128)
def limite_camino(f, a_s, b_s, p):
    g = sp.simplify(f.subs({x: a_s + s, y: b_s + p}, simultaneous=True))
    return g, sp.limit(g, s, 0)


@lru_cache(maxsize=64)
def derivadas_parciales(f):
    return sp.simplify(sp.diff(f, x)), sp.simplify(sp.diff(f, y))
