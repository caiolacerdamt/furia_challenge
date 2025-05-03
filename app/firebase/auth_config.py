import pyrebase
import streamlit as st
import os
from dotenv import load_dotenv

if os.getenv("ENV") == "LOCAL":
    load_dotenv()
    firebase_config = {
        "apiKey": os.getenv("apiKey"),
        "authDomain": os.getenv("authDomain"),
        "databaseURL": os.getenv("databaseURL"),
        "projectId": os.getenv("projectId"),
        "storageBucket": os.getenv("storageBucket"),
        "messagingSenderId": os.getenv("messagingSenderId"),
        "appId": os.getenv("appId"),
        "measurementId": os.getenv("measurementId"),
    }
else:
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

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
