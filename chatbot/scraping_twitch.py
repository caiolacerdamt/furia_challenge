import os
import requests
from dotenv import load_dotenv
import streamlit as st

CLIENT_ID = st.secrets["twitch"]["twitch_client_id"]
ACCESS_TOKEN = st.secrets["twitch"]["twitch_access_token"]

# load_dotenv()
# CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
# ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")

def check_if_live(user_logins):
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    live_users = []
    
    for user in user_logins:
        params = {"user_login": user}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Erro na API Twitch para {user}: {response.status_code} {response.text}")
            continue
        
        data = response.json()
        
        streams = data.get("data", [])
        if streams:
            live_users.append(user)
    
    return live_users
