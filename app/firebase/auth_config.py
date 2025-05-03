import pyrebase
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

get = lambda k: st.secrets[k] if "streamlit" in os.environ.get("HOME", "").lower() else os.getenv(k)

firebase_config = {
    "apiKey": get("FIREBASE_API_KEY"),
    "authDomain": get("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": get("FIREBASE_DB_URL"),
    "projectId": get("FIREBASE_PROJECT_ID"),
    "storageBucket": get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": get("FIREBASE_MESSAGING_ID"),
    "appId": get("FIREBASE_APP_ID"),
    "measurementId": get("FIREBASE_MEASUREMENT_ID"),
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()
