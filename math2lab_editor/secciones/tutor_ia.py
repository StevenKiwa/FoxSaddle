"""Sección Tutor IA: chat con Gemini para explicar ejercicios paso a paso."""
import streamlit as st

from nucleo.ia import MSG_LIMITE, clave_gemini, cupo_ia, flujo_ia, mensaje_error


def tutor_ia(ctx):
    """Chat con memoria: cada pregunta viaja con la función y el punto actuales para que el tutor tenga contexto."""
    f, a, b = ctx.f, ctx.a, ctx.b
    st.subheader("Tutor IA")
    st.caption("Escribe tu ejercicio o tu duda. El tutor conoce la función del editor y el punto (a, b) de la barra lateral.")
    chat = st.session_state.setdefault("chat", [])   # historial de la sesión: [{role, content, mostrar}, ...]
    hay_clave = bool(clave_gemini())                 # se consulta una sola vez por ejecución
    if not hay_clave:
        st.warning("El tutor de IA no está disponible por el momento. Inténtalo más tarde.")
    # Se vuelve a dibujar todo el historial en cada ejecución (Streamlit no conserva lo ya pintado).
    # "mostrar" es lo que ve el usuario; "content" es lo que se envía a la IA (incluye el contexto).
    for m in chat:
        with st.chat_message(m["role"]):
            st.markdown(m["mostrar"])

    pregunta = st.chat_input("Escribe tu ejercicio o tu duda...")
    if pregunta and hay_clave:
        if not cupo_ia():                            # protege la cuota gratuita compartida (límite por sesión)
            st.warning(MSG_LIMITE)
        else:
            contexto = f"(Función actual: f(x,y) = {f}; punto de estudio: ({a}, {b}).)\n\n"
            chat.append({"role": "user", "content": contexto + pregunta, "mostrar": pregunta})
            with st.chat_message("user"):
                st.markdown(pregunta)
            with st.chat_message("assistant"):
                try:                                 # la respuesta aparece por trozos mientras se genera
                    texto = st.write_stream(flujo_ia([{"role": m["role"], "content": m["content"]} for m in chat]))
                except Exception as e:               # error de red o de la API: mensaje amable, sin detalles técnicos
                    texto = mensaje_error(e)
                    st.error(texto)
            chat.append({"role": "assistant", "content": texto, "mostrar": texto})

    if chat and st.button("Borrar conversación"):
        st.session_state.chat = []
        st.rerun()