import pyrebase
import streamlit as st

firebase_config = st.secrets["firebase"]

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()