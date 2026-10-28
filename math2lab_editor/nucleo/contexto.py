"""Datos compartidos por todas las secciones: la función y el punto elegidos en la barra lateral."""
from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class Contexto:
    f: sp.Expr          # función f(x, y) ya interpretada
    a: float            # punto (a, b) al que tiende el límite
    b: float
    a_s: sp.Expr        # a y b en forma exacta de SymPy
    b_s: sp.Expr
    texto_f: str        # texto que escribió el usuario

    @property
    def base(self):
        """Resumen en texto que se envía a la IA como contexto."""
        return f"Función f(x,y) = {self.f}. Punto de estudio (a,b) = ({self.a}, {self.b})."
