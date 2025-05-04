import streamlit as st
from app.pages.cadastro import (
    TelaLogin, TelaCadastro, TelaRecuperarSenha,
    TelaConfirmacaoEmail
)

def render_access():
    with st.spinner("Carregando tela de acesso..."):
        st.container()
        st.markdown(
            "<h1 style='text-align: center;'>FanFURIA 🎮</h1>",
            unsafe_allow_html=True
        )
        st.write("")
        page = st.session_state.get("pagina_acesso", "Login")

        if page == "Login":
            if st.session_state.get("recuperar_senha", False):
                TelaRecuperarSenha().render()
            else:
                TelaLogin().render()
        else:
            TelaCadastro().render()


def render_confirm_email():
    with st.spinner("Confirmando e-mail..."):
        TelaConfirmacaoEmail().render()