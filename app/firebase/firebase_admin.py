import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import json
import streamlit as st

if "type" in st.secrets:
    service_account_dict = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"],
        "universe_domain": st.secrets["universe_domain"]
    }
else:
    from dotenv import load_dotenv
    load_dotenv()
    
    with open("app/firebase/firebase_key.json") as f:
        service_account_dict = json.load(f)

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_dict)
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET", "furia-fans.appspot.com")
    })

db_firebase = firestore.client()
