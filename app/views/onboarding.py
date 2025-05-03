import streamlit as st
from app.pages.cadastro import TelaOnboarding

def render_onboarding():
    with st.spinner("Carregando onboarding..."):
        TelaOnboarding().render()