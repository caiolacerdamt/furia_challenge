import streamlit as st
from app.firebase.firebase_admin import db_firebase
from chatbot.handlers import (
    initialize_state,
    render_history,
    step_inicio,
    step_menu,
    step_loading_streamers,
    step_list_games,
    step_list_teams,
    step_list_players,
    step_calendar,
    step_redes_sociais,
    step_fim,
)

class TelaBase:
    def render(self):
        raise NotImplementedError()

class ChatBot(TelaBase):
    def render(self):
        st.title("Chatbot da FURIA")
        initialize_state()
        render_history()

        step = st.session_state["chatbot_step"]
        {
            "inicio": step_inicio,
            "menu": step_menu,
            "loading_streamers": step_loading_streamers,
            "list_games": step_list_games,
            "list_teams": step_list_teams,
            "list_players": step_list_players,
            "calendar": step_calendar,
            "redes_sociais": step_redes_sociais,
            "fim": step_fim,
        }[step]()