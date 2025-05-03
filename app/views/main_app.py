import streamlit as st
from app.pages.home import HomePage
from app.pages.perfil import TelaPerfil
from app.pages.fans import InstagramPostsRenderer, TweetsRenderer, SocialLinksRenderer
from app.pages.chatbot import ChatBot
from app.utils.session import logout

def render_main_app():
    username = st.session_state.get(
        "nickname", st.session_state.get("user_nome", "Anonymous")
    )
    st.sidebar.markdown(f"👤 Olá, {username}")

    menu_options = {
        "Home": HomePage(),
        "Chat": ChatBot(),
        "Fans": SocialLinksRenderer(),
        "Perfil": TelaPerfil(),
    }
    choice = st.sidebar.selectbox("Menu", list(menu_options.keys()))

    menu_options[choice].render()

    if choice == "Fans":
            InstagramPostsRenderer().render()
            TweetsRenderer().render()

    if st.sidebar.button("🚪 Logout"):
        logout()