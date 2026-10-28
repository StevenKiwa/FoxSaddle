"""Conversión entre el LaTeX del editor visual (MathLive) y el texto que entiende la página (x^2*y/(x^2+y^2))."""
import re

import sympy as sp

FUNCIONES = {"sin": "sin", "cos": "cos", "tan": "tan", "cot": "cot", "sec": "sec", "csc": "csc",
             "arcsin": "asin", "arccos": "acos", "arctan": "atan", "sinh": "sinh", "cosh": "cosh",
             "tanh": "tanh", "ln": "ln", "log": "log", "exp": "exp"}
SIMBOLOS = {"cdot": "*", "times": "*", "div": "/", "pi": "pi", "exponentialE": "E",
            "left": "", "right": "", "displaystyle": "", "textstyle": "", "scriptstyle": ""}
ESPACIOS = set(",;:! ")


def _saltar(s, i):
    while i < len(s) and s[i].isspace():
        i += 1
    return i


def _grupo(s, i):
    """Lee el grupo {...} que empieza en s[i]; devuelve (contenido, posición siguiente)."""
    i = _saltar(s, i)
    if i >= len(s) or s[i] != "{":
        raise ValueError("Fórmula incompleta: falta completar algún recuadro del editor.")
    nivel = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            nivel += 1
        elif s[j] == "}":
            nivel -= 1
            if nivel == 0:
                return s[i + 1:j], j + 1
    raise ValueError("Llaves sin cerrar en la fórmula.")


def _envolver(texto):
    """Pone paréntesis salvo en un número o una sola letra (2 y x quedan igual; xy, x+1 o 2x llevan paréntesis,
    para que 1/xy no se lea como (1/x)·y)."""
    return texto if re.fullmatch(r"\d+(?:\.\d+)?|[A-Za-z]", texto) else f"({texto})"


def _conv(s):
    salida, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            nombre = m.group(1)
            i += m.end()
            if nombre in ("frac", "dfrac", "tfrac"):
                num, i = _grupo(s, i)
                den, i = _grupo(s, i)
                salida.append(f"({_envolver(_conv(num))}/{_envolver(_conv(den))})")
            elif nombre == "sqrt":
                i = _saltar(s, i)
                indice = None
                if s[i:i + 1] == "[":
                    j = s.index("]", i)
                    indice, i = s[i + 1:j], j + 1
                cont, i = _grupo(s, i)
                if indice is None:
                    salida.append(f"raiz({_conv(cont)})")
                else:
                    salida.append(f"({_envolver(_conv(cont))}^(1/{_envolver(_conv(indice))}))")
            elif nombre in ("operatorname", "mathrm"):
                cont, i = _grupo(s, i)
                salida.append(_conv(cont))
            elif nombre in FUNCIONES:
                salida.append(FUNCIONES[nombre])
                if s[_saltar(s, i):_saltar(s, i) + 1] == "^":
                    raise ValueError("Para elevar una función usa paréntesis, por ejemplo (sen(x))^2.")
            elif nombre in SIMBOLOS:
                salida.append(SIMBOLOS[nombre])
            elif nombre in ESPACIOS:
                salida.append(" ")
            elif nombre in "()[]":
                salida.append(nombre)
            elif nombre in "{}":
                pass
            else:
                raise ValueError(f"El editor usó un símbolo que la página no admite: \\{nombre}")
        elif c == "{":
            cont, i = _grupo(s, i)
            salida.append(_envolver(_conv(cont)))
        elif c == "^":
            i = _saltar(s, i + 1)
            if s[i:i + 1] == "{":
                cont, i = _grupo(s, i)
                salida.append("^" + _envolver(_conv(cont)))
            else:
                salida.append("^")
        else:
            salida.append(c)
            i += 1
    return "".join(salida)


def latex_a_texto(latex):
    """LaTeX del editor visual → texto como 'x^2*y/(x^2+y^2)' (listo para la función leer)."""
    s = latex.strip()
    if not s:
        raise ValueError("La fórmula está vacía.")
    if "\\placeholder" in s or re.search(r"\\(?:mathtip|class)", s):
        raise ValueError("Fórmula incompleta: completa los recuadros vacíos del editor.")
    s = re.sub(r"\\(?:left|right)?\\?[|]|\\lvert|\\rvert", "|", s)   # barras de valor absoluto
    partes = s.split("|")
    if len(partes) > 1:
        if len(partes) % 2 == 0:
            raise ValueError("Falta cerrar una barra de valor absoluto.")
        s = partes[0] + "".join(("abs(" if k % 2 == 0 else ")") + p for k, p in enumerate(partes[1:]))
    texto = _conv(s)
    texto = re.sub(r"(?<![A-Za-z0-9.])e(?![A-Za-z0-9])", "E", texto)   # la e de Euler
    texto = re.sub(r"\s+", " ", texto).strip()
    if not texto:
        raise ValueError("La fórmula está vacía.")
    return texto


def texto_a_latex(expr):
    """Expresión de SymPy → LaTeX que el editor visual muestra bien."""
    latex = sp.latex(expr)
    return re.sub(r"(?<![A-Za-z\\])e\^", r"\\exponentialE^", latex)
