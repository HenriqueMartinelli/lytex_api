import requests
from types.client_types import estado_para_sigla

class LytexClient:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api-pay.lytex.com.br/v2/clients"
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    def create_client(self, _json):
        response = requests.post(self.base_url, json=_json, headers=self.headers)
        return response.json()
    
    def create_payload(self, address, client):
        return {
        "type": "pf",
        "name": client.name,
        "treatmentPronoun": "you",
        "cpfCnpj": client.cpf,
        "email": client.email,
        "cellphone": client.cellphone,
        "address": {
            "street": address.street,
            "zone": address.zone,
            "city": address.city,
            "state": estado_para_sigla(address.state),
            "number": address.number,
            "complement": address.complement,
            "zip": address.zip
        },
        "referenceId": client.client_code
        }

