import streamlit as st
from app.pages.cadastro import (
    TelaLogin, TelaCadastro, TelaRecuperarSenha,
    TelaConfirmacaoEmail, TelaOnboarding
)
from app.pages.home import HomePage
from app.pages.perfil import TelaPerfil
from app.pages.fans import InstagramPostsRenderer, TweetsRenderer
#from pages.games import GamesPage
#from pages.fans import FansPage


def main():
    st.set_page_config(layout="wide")

    required_keys = ["user", "usuario_cadastrado"]
    for key in required_keys:
        if key not in st.session_state:
            st.session_state[key] = None

    if not st.session_state.usuario_cadastrado:
        if st.session_state.get("confirmando_email", False):
            TelaConfirmacaoEmail().render()
        else:
            with st.container():
                st.markdown("<h2 style='text-align: center;'>Acesso à Plataforma 🎮</h2>", unsafe_allow_html=True)
                st.write("")

                pagina = st.session_state.get("pagina_acesso", "Login")

                if pagina == "Login":
                    if st.session_state.get("recuperar_senha", False):
                        TelaRecuperarSenha().render()
                    else:
                        TelaLogin().render()
                else:
                    TelaCadastro().render()
    else:
        if st.session_state.get("onboarding_pendente", False):
            TelaOnboarding().render()
            return

        user_name = st.session_state.get("nickname", st.session_state.get("user_nome", "Anonymous"))
        st.sidebar.markdown(f"👤 Olá, {user_name}")
        menu = st.sidebar.selectbox("Menu", ["Home", "Games", "Fans", "Perfil"])

        pages = {
            "Home": HomePage(),
            "Perfil": TelaPerfil(),
            #Games": GamesPage(),
            "Fans": InstagramPostsRenderer()
        }
        pages[menu].render()

        if menu == "Fans":
            tweet_renderer = TweetsRenderer()
            tweet_renderer.render()

        if st.sidebar.button("🚪 Logout"):
            keys_to_remove = [
                "user",
                "usuario_cadastrado",
                "user_email",
                "user_uid",
                "user_token",
                "onboarding_pendente"
            ]
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()