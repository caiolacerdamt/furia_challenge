import requests
import os
from dotenv import load_dotenv
import streamlit as st

IMGUR_CLIENT_ID = st.secrets["imgur"]["imgur_client_id"]
IMGUR_CLIENT_SECRET = st.secrets["imgur"]["imgur_client_secret"]
IMGUR_ACCESS_TOKEN = st.secrets["imgur"]["imgur_access_token"]
IMGUR_REFRESH_TOKEN = st.secrets["imgur"]["imgur_refresh_token"]

def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf)) 
    if len(cpf) != 11 or cpf == cpf[0] * 11:  
        return False

    def calcular_digito(cpf_parcial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial) + 1, 1, -1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    primeiro_digito = calcular_digito(cpf[:9])
    segundo_digito = calcular_digito(cpf[:9] + primeiro_digito)

    return cpf[-2:] == primeiro_digito + segundo_digito

def upload_to_imgur(image_data: str, data_type: str = 'url') -> str:
    headers = {'Authorization': f'Bearer {IMGUR_ACCESS_TOKEN}'}
    payload = {'image': image_data, 'type': data_type}
    url = 'https://api.imgur.com/3/upload'

    resp = requests.post(url, headers=headers, data=payload)
    resp.raise_for_status()

    return resp.json()['data']['link']
