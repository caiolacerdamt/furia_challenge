import streamlit as st
from app.pages.home import HomePage
from app.pages.perfil import TelaPerfil
from app.pages.fans import InstagramPostsRenderer, TweetsRenderer, SocialLinksRenderer
from app.pages.chatbot import ChatBot
from app.utils.session import logout
from app.utils.constants import DEFAULT_AVATAR

def render_main_app():

    avatar_url = st.session_state.get("avatar_url", DEFAULT_AVATAR)
    username = st.session_state.get(
        "nickname", st.session_state.get("user_nome", "Anonymous")
    )

    st.sidebar.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <img src="{avatar_url}" width="40" height="40" style="border-radius: 50%;" />
            <span style="font-weight: 600; font-size: 1.1rem;">{username}</span>
        </div>
        """, unsafe_allow_html=True)

    menu_options = {
        "🏠 Home": HomePage(),
        "💬 Chat": ChatBot(),
        "🌟 Fans": SocialLinksRenderer(),
        "👤 Perfil": TelaPerfil(),
    }

    choice = st.sidebar.selectbox("Navegar", list(menu_options.keys()))
    menu_options[choice].render()

    if choice == "🌟 Fans":
        InstagramPostsRenderer().render()
        TweetsRenderer().render()

    st.sidebar.markdown("<div style='height: 590px;'></div>", unsafe_allow_html=True)

    with st.sidebar.container():
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
