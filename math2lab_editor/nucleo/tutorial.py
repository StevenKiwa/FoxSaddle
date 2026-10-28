"""Tutorial guiado de primera visita (se recuerda en el navegador con streamlit-js-eval)."""
import streamlit as st

# Para recordar que el usuario ya lo vio (aunque cierre el navegador) se usa el almacenamiento del navegador
# con la librería streamlit-js-eval. Si no está instalada, el tutorial se ofrece en cada sesión nueva.
try:
    from streamlit_js_eval import streamlit_js_eval
    HAY_LS = True
except Exception:
    HAY_LS = False

CLAVE_LS = "math2lab_tutorial_visto"
PASOS = [
    ("Inicio", "El editor de fórmulas y la barra lateral",
     "**Arriba** está el editor: escribe tu función f(x, y) como en papel (con `/` se crea una fracción, con `^` una "
     "potencia, con `sqrt` una raíz) o usa los botones. Pulsa **Enter** o **Aplicar ✓** para actualizar las gráficas.\n\n"
     "**En la barra lateral** eliges la **sección** y defines el **punto (a, b)** al que tiende el límite.\n\n"
     "Todas las secciones usan esa función y ese punto."),
    ("Inicio", "Inicio",
     "Muestra tu función en notación matemática y las **dos gráficas del ejercicio**: un mapa 2D del plano xy "
     "(con los ejes x, -x, y, -y) y la superficie 3D (con x, -x, y, -y, z, -z)."),
    ("Gráfica 2D y 3D", "Gráfica 2D y 3D",
     "Cambia el **rango** para acercarte o alejarte. La gráfica 3D se gira con el mouse y se acerca con la rueda. "
     "El punto lima marca (a, b, f(a, b)). Los ejes avanzan de 1 en 1 y el botón **Decimales** (esquina "
     "inferior derecha de cada gráfica) alterna entre números enteros y decimales."),
    ("Curvas de nivel", "Curvas de nivel",
     "Dibuja las curvas donde f(x, y) = c. Ajusta la cantidad de curvas y el rango, o activa *Mostrar solo una "
     "curva* para fijar un valor de c. Si curvas de niveles distintos se juntan cerca del punto, el límite podría "
     "no existir. El botón de IA explica cómo interpretarlas."),
    ("Superficies de nivel", "Superficies de nivel",
     "Es para funciones de tres variables w = f(x, y, z). Escribe w, el nivel mínimo y el máximo, y cuántas "
     "superficies dibujar."),
    ("Límite por trayectorias", "Límite por trayectorias",
     "Te acercas al punto por distintos caminos (rectas con pendiente m y curvas). Si dos caminos dan valores "
     "distintos, el límite **no existe**. Si todos coinciden, es solo una pista: no demuestra que exista."),
    ("Límite en coordenadas polares", "Coordenadas polares",
     "Cambia a x = a + r·cos θ, y = b + r·sen θ y hace r → 0⁺. Si el resultado **no depende de θ**, el límite "
     "existe; si depende de θ, no existe."),
    ("Demostración ε-δ", "Demostración ε-δ",
     "Es la demostración formal: para cada ε > 0 se busca un δ > 0 que cumpla la definición del límite. "
     "Úsala cuando necesites el rigor de una demostración."),
    ("Derivadas parciales", "Derivadas parciales",
     "Calcula ∂f/∂x y ∂f/∂y de forma simbólica y muestra otra vez las dos gráficas. El botón de IA explica "
     "cómo se obtuvieron, paso a paso."),
    ("Tutor IA", "Tutor IA",
     "Un chat con Gemini: escribe tu ejercicio o tu duda y recibe una explicación paso a paso. Ve la función y el "
     "punto de la barra lateral y recuerda la conversación. Si la IA está saturada, reintenta sola; si no "
     "responde, espera un minuto."),
]


def _ya_visto():
    """True/False según el navegador; None mientras se está leyendo."""
    if "tut_visto" in st.session_state:
        return st.session_state.tut_visto
    if HAY_LS:
        with st.sidebar:
            v = streamlit_js_eval(js_expressions=f"localStorage.getItem('{CLAVE_LS}') || 'no'", key="ls_leer")
        if v is None:
            return None
        st.session_state.tut_visto = (v == "si")
    else:
        st.session_state.tut_visto = False
    return st.session_state.tut_visto


def _cerrar_tutorial():
    st.session_state.tut_estado = "cerrado"
    st.session_state.tut_visto = True
    st.session_state.tut_guardar = True      # se guarda en el navegador para no volver a ofrecerlo


def _ir_paso(paso):
    paso = max(0, min(paso, len(PASOS) - 1))
    st.session_state.tut_paso = paso
    st.session_state.seccion = PASOS[paso][0]    # el tutorial cambia de sección automáticamente


def empezar_tutorial():
    st.session_state.tut_estado = "activo"
    _ir_paso(0)


def tutorial():
    if st.session_state.get("tut_guardar") and HAY_LS:
        with st.sidebar:
            streamlit_js_eval(js_expressions=f"localStorage.setItem('{CLAVE_LS}','si')", key="ls_guardar")
    if "tut_estado" not in st.session_state:
        visto = _ya_visto()
        if visto is None:
            return                               # todavía leyendo el navegador
        st.session_state.tut_estado = "cerrado" if visto else "oferta"
    estado = st.session_state.tut_estado
    if estado == "cerrado":
        return

    try:
        caja = st.container(border=True)
    except TypeError:
        caja = st.container()
    with caja:
        if estado == "oferta":
            st.markdown("### ¡Bienvenido a FoxSaddle!")
            st.write("¿Quieres un **tutorial guiado**? Te muestro para qué sirve cada sección (menos de 2 minutos). "
                     "Solo te lo ofrezco esta primera vez; podrás repetirlo cuando quieras con el botón "
                     "**❓ Ver tutorial** de la barra lateral.")
            c1, c2, _ = st.columns([1, 1, 2])
            c1.button("Sí, guíame", type="primary", on_click=empezar_tutorial, key="tut_si")
            c2.button("No, gracias", on_click=_cerrar_tutorial, key="tut_no")
        else:
            paso = st.session_state.get("tut_paso", 0)
            _, titulo, texto = PASOS[paso]
            st.progress((paso + 1) / len(PASOS))
            st.caption(f"Tutorial · paso {paso + 1} de {len(PASOS)}")
            st.markdown(f"### {titulo}")
            st.markdown(texto)
            c1, c2, c3, _ = st.columns([1, 1, 1, 1])
            c1.button("← Anterior", disabled=(paso == 0), on_click=_ir_paso, args=(paso - 1,), key="tut_ant")
            if paso < len(PASOS) - 1:
                c2.button("Siguiente →", type="primary", on_click=_ir_paso, args=(paso + 1,), key="tut_sig")
            else:
                c2.button("Finalizar ✔", type="primary", on_click=_cerrar_tutorial, key="tut_fin")
            c3.button("Salir", on_click=_cerrar_tutorial, key="tut_salir")
