import requests
import os
from dotenv import load_dotenv

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

def upload_to_imgur(image_url: str) -> str:
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    data = {"image": image_url, "type": "url"}  
    response = requests.post("https://api.imgur.com/3/image", headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        print(f"Erro ao fazer upload para o Imgur: {response.status_code}, {response.text}")
        return ""