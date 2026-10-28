
import streamlit as st

from nucleo.ia import MSG_LIMITE, clave_gemini, cupo_ia, flujo_ia, mensaje_error


def tutor_ia(ctx):
    f, a, b = ctx.f, ctx.a, ctx.b
    st.subheader("Tutor IA")
    st.caption("Escribe tu ejercicio o tu duda. El tutor conoce la función del editor y el punto (a, b) de la barra lateral.")
    chat = st.session_state.setdefault("chat", [])   
    hay_clave = bool(clave_gemini())                
    if not hay_clave:
        st.warning("El tutor de IA no está disponible por el momento. Inténtalo más tarde.")
    for m in chat:
        with st.chat_message(m["role"]):
            st.markdown(m["mostrar"])

    pregunta = st.chat_input("Escribe tu ejercicio o tu duda...")
    if pregunta and hay_clave:
        if not cupo_ia():                           
            st.warning(MSG_LIMITE)
        else:
            contexto = f"(Función actual: f(x,y) = {f}; punto de estudio: ({a}, {b}).)\n\n"
            chat.append({"role": "user", "content": contexto + pregunta, "mostrar": pregunta})
            with st.chat_message("user"):
                st.markdown(pregunta)
            with st.chat_message("assistant"):
                try:                                 
                    texto = st.write_stream(flujo_ia([{"role": m["role"], "content": m["content"]} for m in chat]))
                except Exception as e:               
                    texto = mensaje_error(e)
                    st.error(texto)
            chat.append({"role": "assistant", "content": texto, "mostrar": texto})

    if chat and st.button("Borrar conversación"):
        st.session_state.chat = []
        st.rerun()
