import streamlit as st
from app.utils.session import init_session_state
from app.views.access import render_access, render_confirm_email
from app.views.onboarding import render_onboarding
from app.views.main_app import render_main_app

def main():
    st.set_page_config(layout="wide")

    init_session_state({
        "user": None,
        "usuario_cadastrado": None,
        "confirmando_email": False,
        "recuperar_senha": False,
        "pagina_acesso": "Login",
        "onboarding_pendente": False,
    })

    if not st.session_state.usuario_cadastrado:
        if st.session_state.confirmando_email:
            render_confirm_email()
        else:
            render_access()
    else:
        if st.session_state.onboarding_pendente:
            render_onboarding()
        else:
            render_main_app()

if __name__ == "__main__":
    main()