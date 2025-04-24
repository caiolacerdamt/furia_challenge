import streamlit as st
from app.pages import cadastro
from app.pages import home, fans, games

def main():
    if "usuario_cadastrado" not in st.session_state:
        st.session_state.usuario_cadastrado = False

    if not st.session_state.usuario_cadastrado:
        if st.session_state.get("confirmando_email"):
            cadastro.tela_confirmacao_email()
        else:
            aba = st.sidebar.radio("Acesso", ["Login", "Cadastro"])
            if aba == "Login":
                if st.session_state.get("recuperar_senha"):
                    cadastro.tela_recuperar_senha()
                else:
                    cadastro.tela_login()
            else:
                cadastro.tela_cadastro()
    
    else:
        st.sidebar.markdown(f"👤 Fala, Furioso")

        menu = st.sidebar.selectbox("Menu", ["Home", "Games", "Fans"])
        if menu == "Home":
            home.display_home()
        elif menu == "Games":
            games.display_games()
        elif menu == "Fans":
            fans.display_fans()

        if st.sidebar.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()


