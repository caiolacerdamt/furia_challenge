import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

get = lambda k: st.secrets[k] if "streamlit" in os.environ.get("HOME", "").lower() else os.getenv(k)

if not firebase_admin._apps:
    service_account_dict = {
        "type": get("TYPE"),
        "project_id": get("PROJECT_ID"),
        "private_key_id": get("PRIVATE_KEY_ID"),
        "private_key": get("PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": get("CLIENT_EMAIL"),
        "client_id": get("CLIENT_ID"),
        "auth_uri": get("AUTH_URI"),
        "token_uri": get("TOKEN_URI"),
        "auth_provider_x509_cert_url": get("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": get("CLIENT_X509_CERT_URL"),
        "universe_domain": get("UNIVERSE_DOMAIN")
    }

    cred = credentials.Certificate(service_account_dict)
    firebase_admin.initialize_app(cred, {
        'storageBucket': get("FIREBASE_STORAGE_BUCKET")
    })

db_firebase = firestore.client()
