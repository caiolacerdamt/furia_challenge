import requests
import os
from dotenv import load_dotenv
from app.firebase.firebase_admin import db_firebase

load_dotenv()

def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(cpf_parcial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf_parcial, range(len(cpf_parcial)+1, 1, -1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    primeiro_digito = calcular_digito(cpf[:9])
    segundo_digito = calcular_digito(cpf[:9] + primeiro_digito)

    return cpf[-2:] == primeiro_digito + segundo_digito

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")

def upload_to_imgur(image_data: str, data_type="url") -> str:
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    payload = {"image": image_data, "type": data_type}
    url = "https://api.imgur.com/3/upload"
    response = requests.post(url, headers=headers, data=payload)
    if response.ok:
        return response.json()["data"]["link"]
    else:
        raise Exception(f"Imgur upload failed: {response.status_code}, {response.text}")
    