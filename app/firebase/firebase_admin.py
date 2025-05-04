import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
import tempfile
import os

if not firebase_admin._apps:

    creds_dict = dict(st.secrets["firebase_admin"])

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        json.dump(creds_dict, f)
        f.flush()
        temp_cred_path = f.name

    cred = credentials.Certificate(temp_cred_path)
    firebase_admin.initialize_app(cred, {})

    os.remove(temp_cred_path)

db_firebase = firestore.client()