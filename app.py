import streamlit as st
from app.pages import cadastro
from app.pages import home, fans, games

def main():
    if "usuario_cadastrado" not in st.session_state:
        st.session_state.usuario_cadastrado = False

    if not st.session_state.usuario_cadastrado:
        aba = st.sidebar.radio("Acesso", ["Login", "Cadastro"])
        if aba == "Login":
            cadastro.tela_login()
        else:
            cadastro.tela_cadastro()
    
    else:
        st.sidebar.markdown(f"👤 Olá, **{st.session_state.get('user_nome', 'Usuário')}**")

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

