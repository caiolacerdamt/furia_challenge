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
        "apiKey": st.secrets["AUTH"]["apiKey"],
        "authDomain": st.secrets["AUTH"]["authDomain"],
        "databaseURL": st.secrets["AUTH"]["databaseURL"],
        "projectId": st.secrets["AUTH"]["projectId"],
        "storageBucket": st.secrets["AUTH"]["storageBucket"],
        "messagingSenderId": st.secrets["AUTH"]["messagingSenderId"],
        "appId": st.secrets["AUTH"]["appId"],
        "measurementId": st.secrets["AUTH"]["measurementId"],
    }

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
