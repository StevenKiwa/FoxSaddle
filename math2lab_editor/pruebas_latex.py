"""Prueba rápida del conversor de LaTeX. Ejecutar:  python pruebas_latex.py"""
import sympy as sp

from nucleo.latex import latex_a_texto, texto_a_latex
from nucleo.matematica import leer

CASOS = [   # (lo que entrega el editor, la función que debe resultar)
    (r"\frac{x^2y}{x^2+y^2}", "x**2*y/(x**2+y**2)"),
    (r"\frac{x^{2}\cdot y}{x^{2}+y^{2}}", "x**2*y/(x**2+y**2)"),
    (r"\frac{xy}{\sqrt{x^2+y^2}}", "x*y/sqrt(x**2+y**2)"),
    (r"\frac{\sin\left(x^2+y^2\right)}{x^2+y^2}", "sin(x**2+y**2)/(x**2+y**2)"),
    (r"\frac{\sin\left(xy\right)}{xy}", "sin(x*y)/(x*y)"),
    (r"\exponentialE^{-x^2-y^2}", "exp(-x**2-y**2)"),
    (r"e^{-x^2-y^2}", "exp(-x**2-y**2)"),
    (r"\sqrt{x^2+y^2}", "sqrt(x**2+y**2)"),
    (r"\left|x\right|+\left|y\right|", "Abs(x)+Abs(y)"),
    (r"\frac{\left(x^2-1\right)y}{x-1}", "(x**2-1)*y/(x-1)"),
    (r"x^2-y^2", "x**2-y**2"),
    (r"\ln\left(x^2+y^2+1\right)", "log(x**2+y**2+1)"),
    (r"\sqrt[3]{x}+y", "x**(1/3)+y"),
    (r"\pi x+\frac{1}{2}y", "pi*x+y/2"),
    (r"\sin\left(x\right)\cos\left(y\right)", "sin(x)*cos(y)"),
    (r"\frac{x^3+y^3}{x^2+y^2}", "(x**3+y**3)/(x**2+y**2)"),
    (r"x^2+y^2+z^2", "x**2+y**2+z**2"),
]
RECHAZOS = [r"\int x\,dx", r"\frac{x}{", r"\frac{\placeholder{}}{y}", r"a+b", r"\theta x", "", r"\sin^2\left(x\right)"]

fallos = 0
for latex, esperado in CASOS:
    try:
        texto = latex_a_texto(latex)
        ok = sp.simplify(leer(texto) - leer(esperado)) == 0
    except Exception as e:
        texto, ok = f"ERROR {e}", False
    fallos += not ok
    print("OK   " if ok else "FALLA", latex, "->", texto)
for latex in RECHAZOS:
    try:
        leer(latex_a_texto(latex)); print("FALLA (debía rechazarse):", latex); fallos += 1
    except Exception as e:
        print("OK    rechazado:", latex or "(vacío)", "|", str(e)[:70])
# ida y vuelta: texto -> LaTeX del editor -> texto
for t in ["x^2*y/(x^2+y^2)", "sen(x*y)/(x*y)", "exp(-x^2-y^2)", "raiz(x^2+y^2)", "abs(x)+abs(y)", "x^2-y^2"]:
    f = leer(t)
    f2 = leer(latex_a_texto(texto_a_latex(f)))
    ok = sp.simplify(f - f2) == 0
    fallos += not ok
    print("OK   " if ok else "FALLA", "ida y vuelta:", t, "->", texto_a_latex(f))
print("\nFallos:", fallos)
