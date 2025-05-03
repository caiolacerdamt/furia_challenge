import streamlit as st

def init_session_state(defaults: dict):
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

def logout():
    keys_to_remove = [
        "user", "usuario_cadastrado", "user_email",
        "user_uid", "user_token", "onboarding_pendente"
    ]
    for key in keys_to_remove:
        st.session_state.pop(key, None)
    st.rerun()