from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class Contexto:
    f: sp.Expr
    a: float
    b: float
    a_s: sp.Expr
    b_s: sp.Expr
    texto_f: str

    @property
    def base(self):
        return f"Función f(x,y) = {self.f}. Punto de estudio (a,b) = ({self.a}, {self.b})."
