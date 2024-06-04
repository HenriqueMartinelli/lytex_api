import json
import requests
import pandas as pd
from datetime import datetime
from typing import NamedTuple
from datetime import datetime, timezone

from produto import *
from auth.lytexAuth import LyTexAuth


class ContratoController:
    def __init__(self, bearer_token):
        self.session = requests.Session()
        self.headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {bearer_token}'
        }

    def pegar_id_pessoa(self, cpf):
        params = {
            'search': cpf.replace(".", "").replace("-", ""),
        }
        pegar_id = self.session.get(url='https://api-pay.lytex.com.br/v2/clients', 
                                    params=params, 
                                    headers=self.headers, 
                                    timeout=20)
        if pegar_id.json().get("results") == []:
            print(cpf)
            raise ValueError("Cliente não cadastrado")
        if self.verificar_token_expirado(pegar_id.json()): return pegar_id.json()
        resultado = pegar_id.json()["results"][0]
        resultado["id"] = resultado["_id"]
        resultado.pop('_id', None)
        return resultado
    
    def verificar_token_expirado(self, response):
        if response.get("message"):
            if response.get("message") == "Token expirado":
                return True
        return False

    def criar_contrato(self, clienteApi, cliente):
        tres_da_manha = datetime.now().replace(hour=3, minute=0, second=0, microsecond=0)

        data_formatada = tres_da_manha.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        with open("configs/contrato.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)

        json_data["client"].update({
            "name": clienteApi.name,
            "treatmentPronoun": clienteApi.treatmentPronoun,
            "type": clienteApi.type,
            "cpfCnpj": clienteApi.cpfCnpj,
            "cellphone": clienteApi.cellphone,
            "createdAt": clienteApi.createdAt,
            "email": clienteApi.email
        })

        json_data["recurrence"]["nextAt"] = data_formatada
        json_data["duration"]["value"] = cliente.quantParcelas
        json_data["items"][0]["value"] = cliente.valorServico.replace(",","").replace(".", "")
        json_data["items"][0]["_productId"] = None

        json_data["observation"] = (
            "🚀Cobrança de honorários sobre a "
            "implementação do Piso Nacional, Matrícula {}, "
            "por 12 meses, incluindo 13o. " 
            "Conforme contrato, o percentual de 20% é exclusivo aos filiados da AFPEB/ACEB, "
            "de modo que, ao pagar o boleto, concorda em ser feito o desconto da mensalidade🚀"
        ).format(cliente.matricula) 

        
        response = self.session.post(url='https://api-pay.lytex.com.br/v2/subscriptions',
                                    headers=self.headers,
                                    json=json_data,
                                    timeout=20)
        if self.verificar_token_expirado(response.json()): return response.json()
        return json_data

