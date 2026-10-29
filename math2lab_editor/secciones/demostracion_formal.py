
import numpy as np
import streamlit as st
import sympy as sp

from nucleo.ia import bloque_ia
from nucleo.matematica import evaluar, leer, limite_polar, r, t


def _termino_principal(d):

    try:
        serie = sp.expand(sp.series(d, r, 0, 9).removeO())
        for k in range(9):
            c = sp.simplify(serie.coeff(r, k))
            if c != 0:
                return (k, c) if k >= 1 else (None, None)
    except Exception:
        pass
    return None, None


def _sup_numerico(d, rho):

    ths = np.linspace(0, 2 * np.pi, 721)
    try:
        with np.errstate(all="ignore"):
            v = np.abs(np.array(sp.lambdify((r, t), d, "numpy")(rho, ths), dtype=float) * np.ones_like(ths))
        v = v[np.isfinite(v)]
        return float(v.max()) if v.size else None
    except Exception:
        return None


def _orden_numerico(d):

    s1, s2 = _sup_numerico(d, 0.1), _sup_numerico(d, 0.01)
    if not s1 or not s2:
        return None
    k = float(np.log10(s1 / s2))
    return next((kk for kk in range(1, 7) if abs(k - kk) < 0.2), None)


def _cota_numerica(d, k):

    rs, ths = np.linspace(1e-3, 1, 300)[:, None], np.linspace(0, 2 * np.pi, 721)[None, :]
    with np.errstate(all="ignore"):
        vals = np.abs(np.array(sp.lambdify((r, t), d / r**k, "numpy")(rs, ths), dtype=float) * np.ones((300, 721)))
    vals = vals[np.isfinite(vals)]
    return float(np.ceil(vals.max() * 1000) / 1000) if vals.size and vals.max() > 0 else 0.0



def _mostrar_definicion():

    st.info("**Definición.** Sea f una función de dos variables definida en un disco abierto "
            "B((x₀, y₀); r), excepto posiblemente en (x₀, y₀). El límite de f(x, y) cuando (x, y) → (x₀, y₀) es L, "
            "y se escribe lim f(x, y) = L, si para todo ε > 0, por pequeño que sea, existe δ > 0 tal que "
            "|f(x, y) − L| < ε siempre que 0 < √((x − x₀)² + (y − y₀)²) < δ.")


def _pedir_L_y_epsilon(ctx, lim):
    """Pide L (por defecto, el límite que ya calculó la sección de polares) y ε. Devuelve (L, ε)."""

    L_auto = str(lim) if (not lim.has(t) and lim.is_finite) else "0"
    c1, c2 = st.columns(2)

    L = sp.nsimplify(leer(c1.text_input("Valor del límite L", L_auto, key=f"L_{ctx.texto_f}_{ctx.a}_{ctx.b}")))
    eps = c2.number_input("ε (para la verificación numérica)", value=0.1, min_value=1e-6, format="%.4f")
    return L, eps


def _paso1(g, L):
    """Paso 1: la diferencia f − L en polares (g ya es f en polares). Devuelve d."""
    st.markdown("**Paso 1. Diferencia a acotar** (con u = x − x₀, v = y − y₀, ρ = √(u² + v²) y coordenadas polares):")
    d = sp.simplify(g - L)
    st.latex(r"|f(x,y)-L| = \left|" + sp.latex(d) + r"\right|")
    return d


def _orden_de_la_diferencia(d):
    """Busca k y h(θ) tales que |d| ≈ ρᵏ·|h(θ)|. Devuelve (k, h, exacto); k es None si ningún método funciona.
    Tres estrategias, de la más a la menos rigurosa:
      1. exacta: d / ρᵏ no contiene ρ (k = 1, 2 o 3);
      2. término principal del desarrollo en serie en ρ (SymPy);
      3. plan B numérico: se estima k comparando ρ = 0.1 con ρ = 0.01 (h queda desconocida)."""
    for kk in (1, 2, 3):
        hh = sp.simplify(d / r**kk)
        if not hh.has(r):
            return kk, hh, True
    k, h = _termino_principal(d)
    if k is None:
        return _orden_numerico(d), None, False
    return k, h, False


def _error_sin_cota(d, L, a, b):
    """No se pudo acotar la diferencia: distingue 'L o el punto están mal' de 'límite del método'."""
    resto = _sup_numerico(d, 1e-3)                  
    if resto is not None and resto > 1e-2:
        st.error(f"Con L = {L}, la diferencia |f − L| no tiende a 0: vale ≈ {resto:.3g} muy cerca del punto "
                 f"({a}, {b}). Revisa el valor de L, el punto (a, b) o si el límite existe (usa trayectorias y polares).")
    else:
        st.error("Este método automático no pudo acotar la diferencia como ρᵏ·h(θ). "
                 "Revisa si L es correcto o si el límite existe (usa trayectorias y polares).")


def _pasos_2_y_3(d, k, h, exacto):
    """Pasos 2 y 3: muestra el orden de la diferencia y acota la parte angular. Devuelve la cota M."""
    if exacto:
        st.markdown("**Paso 2. Factorizar la potencia de ρ:**")
        st.latex(rf"|f(x,y)-L| = \rho^{{{k}}}\,\left|{sp.latex(h)}\right|")

        ths = np.linspace(0, 2 * np.pi, 4001)
        with np.errstate(all="ignore"):
            vals = np.abs(np.array(sp.lambdify(t, h, "numpy")(ths), dtype=float) * np.ones_like(ths))
        vals = vals[np.isfinite(vals)]
        M = float(np.ceil(vals.max() * 1000) / 1000) if vals.size and vals.max() > 0 else 0.0
        st.markdown("**Paso 3. Acotar la parte angular** (|sen θ| ≤ 1 y |cos θ| ≤ 1):")
        st.latex(rf"\left|{sp.latex(h)}\right| \le M = {M:.3f}")
        st.caption("M se obtuvo evaluando la expresión en 4001 ángulos; justifícalo analíticamente con |sen θ|, |cos θ| ≤ 1.")
        return M
    st.markdown("**Paso 2. Orden de la diferencia** (desarrollo en serie en ρ; término principal):")
    if h is not None:
        st.latex(rf"|f(x,y)-L| = \rho^{{{k}}}\,\left|{sp.latex(h)} + O(\rho)\right|")
    else:
        st.latex(rf"|f(x,y)-L| = O\left(\rho^{{{k}}}\right)")
        st.caption("SymPy no pudo desarrollar la serie en ρ; el orden k se estimó numéricamente.")
    M = _cota_numerica(d, k)
    st.markdown("**Paso 3. Acotar el cociente** para 0 < ρ ≤ 1:")
    st.latex(rf"\left|\frac{{f(x,y)-L}}{{\rho^{{{k}}}}}\right| \le M = {M:.3f}")
    st.caption("Esta diferencia no es una sola potencia de ρ, así que M se obtuvo evaluando numéricamente en una malla "
               "de ρ ∈ (0, 1] y θ. Justifícalo analíticamente (por ejemplo con |sen u| ≤ |u| o 1 − e⁻ᵘ ≤ u).")
    return M


def _paso4_delta(k, M, eps, exacto):
    """Paso 4: δ en función de ε. Con M exacta, δ = (ε/M)^(1/k); con M numérica se limita además a 1
    (la cota solo se comprobó para ρ ≤ 1). Devuelve δ."""
    st.markdown("**Paso 4. Elegir δ en función de ε:**")
    if M <= 0:                                      
        st.latex(r"\delta = 1\ (\text{cualquier } \delta>0)")
        return 1.0
    if exacto:
        st.latex(r"\delta=\left(\frac{\varepsilon}{M}\right)^{1/%d}" % k + rf"=\left(\frac{{\varepsilon}}{{{M:.3f}}}\right)^{{1/{k}}}")
        return (eps / M) ** (1 / k)
    st.latex(r"\delta=\min\left\{1,\left(\frac{\varepsilon}{M}\right)^{1/%d}\right\}" % k
             + rf"=\min\left\{{1,\left(\frac{{\varepsilon}}{{{M:.3f}}}\right)^{{1/{k}}}\right\}}")
    return min(1.0, (eps / M) ** (1 / k))


def _paso5_conclusion(k, h, L, a, b, exacto):
    """Paso 5: cadena de desigualdades que cierra la demostración y mensaje final."""
    st.markdown("**Paso 5. Conclusión:** si 0 < ρ < δ, entonces")
    if exacto:
        st.latex(rf"|f(x,y)-L| = \rho^{{{k}}}\left|{sp.latex(h)}\right| \le M\rho^{{{k}}} < M\delta^{{{k}}} = \varepsilon \quad\blacksquare")
    else:
        st.latex(rf"|f(x,y)-L| \le M\rho^{{{k}}} < M\delta^{{{k}}} \le \varepsilon \quad\blacksquare")
    st.success(f"Por lo tanto, lim f(x, y) = {L} cuando (x, y) → ({a}, {b}).")


def _verificacion_numerica(f, a, b, L, delta, eps):
    """Comprobación independiente: 20 000 puntos al azar dentro del disco de radio δ; |f − L| debería ser < ε.
    Es evidencia complementaria, no sustituye la demostración."""
    n = 20000
    rg = np.random.default_rng(0)                   
    rad, ang = delta * np.sqrt(rg.random(n)), rg.random(n) * 2 * np.pi   
    Z = evaluar(f, float(a) + rad * np.cos(ang), float(b) + rad * np.sin(ang))
    Z = Z[np.isfinite(Z)]
    peor = float(np.max(np.abs(Z - float(L)))) if Z.size else float("nan")
    c1, c2 = st.columns(2)
    c1.metric(f"δ calculado para ε = {eps}", f"{delta:.5f}")
    c2.metric("Mayor |f − L| en el disco de radio δ", f"{peor:.5f}")
    st.caption("Verificación numérica con 20 000 puntos: evidencia complementaria, no sustituye la demostración.")



def demostracion_formal(ctx):
    """Demostración ε-δ paso a paso para el límite de f en (a, b) con el L que indique el usuario."""
    f, a, b = ctx.f, ctx.a, ctx.b
    st.subheader("Demostración formal del límite con ε y δ")
    _mostrar_definicion()
    g, lim = limite_polar(f, ctx.a_s, ctx.b_s)     
    L, eps = _pedir_L_y_epsilon(ctx, lim)
    d = _paso1(g, L)
    k, h, exacto = _orden_de_la_diferencia(d)
    if k is None:
        _error_sin_cota(d, L, a, b)
        return
    M = _pasos_2_y_3(d, k, h, exacto)
    delta = _paso4_delta(k, M, eps, exacto)
    _paso5_conclusion(k, h, L, a, b, exacto)
    _verificacion_numerica(f, a, b, L, delta, eps)
    bloque_ia(ctx.base + f" Límite propuesto L = {L}. Diferencia en polares: |f−L| ≈ ρ^{k}·|{h}|, "
              f"con cota M = {M:.3f} y δ = (ε/M)^(1/{k}). Explica esta demostración ε-δ paso a paso, "
              "justificando la cota de la parte angular.", "ia_ed")
