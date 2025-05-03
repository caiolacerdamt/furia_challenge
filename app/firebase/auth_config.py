import pyrebase
import streamlit as st
import os
from dotenv import load_dotenv

if "apiKey" in st.secrets:
    firebase_config = {
        "apiKey": st.secrets["apiKey"],
        "authDomain": st.secrets["authDomain"],
        "databaseURL": st.secrets["databaseURL"],
        "projectId": st.secrets["projectId"],
        "storageBucket": st.secrets["storageBucket"],
        "messagingSenderId": st.secrets["messagingSenderId"],
        "appId": st.secrets["appId"],
        "measurementId": st.secrets["measurementId"],
    }
else:
    load_dotenv()
    firebase_config = {
        "apiKey": os.getenv("API_KEY"),
        "authDomain": os.getenv("AUTH_DOMAIN"),
        "databaseURL": os.getenv("DATABASE_URL"),
        "projectId": os.getenv("PROJECT_ID"),
        "storageBucket": os.getenv("STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
        "appId": os.getenv("APP_ID"),
        "measurementId": os.getenv("MEASUREMENT_ID"),
    }

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
