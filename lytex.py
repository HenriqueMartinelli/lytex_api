import requests
import pandas as pd
from datetime import datetime
from typing import NamedTuple


class Address(NamedTuple):
    street: str
    zone: str
    city: str
    state: str
    number: str
    complement: str
    zip: str

class Cliente(NamedTuple):
    type: str
    name: str
    cpfCnpj: str
    email: str
    cellphone: str
    address: Address
    referenceId: str


class VendaController:
    def __init__(self, bearer_token):
        self.session = requests.Session()
        self.headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {bearer_token}'
        }

    def pegar_id_pessoa(self, cpf):
        params = {
            'document': cpf,
        }
        pegar_id = self.session.get(url='https://api.contaazul.com/v1/customers', 
                                    params=params, 
                                    headers=self.headers, 
                                    timeout=20)
        if type(pegar_id.json()) != list:
            if pegar_id.json().get("message"):
                raise ValueError(pegar_id.json().get("message"))
        return pegar_id.json()[0]

    def criar_venda(self, id, valor, parcelas, matricula):
        json_data = {
            'emission': '2024-04-23T00:19:50.22',
            'status': 'COMMITTED',
            'scheduled': 'true',
            'customer_id': id,
            'seller_id': 'f4bc0b36-a072-48f5-a6df-07e011ea9021',
            'services': [
                {
                "description": f'Referente a Matrícula {matricula}',
                "quantity": parcelas,
                "service_id": 'd87cca2e-baeb-4523-abb5-29fe9a2ebf52',
                "value": valor,
                }
            ],
            "due_day": 27,
            "hasBillet": "true",
            "duration": parcelas,
        }
        return self.session.post(url='https://api.contaazul.com/v1/contracts', 
                                headers=self.headers, 
                                json=json_data, 
                                timeout=20)

    def fila_de_venda(self, id_pessoa, valor, parcelas, matricula):
        resultado_venda = self.criar_venda(id_pessoa, valor, parcelas, matricula)
        if resultado_venda.json().get("message"):
            return {
                "error": True,
                "msg": resultado_venda.json().get("message")
            }
        return {
            "error": False,
        }

    def processar_cliente(self, cliente):
        if cliente.quant_parcelas > 48:
            return {
            "error": False,
            "numeroParcela": cliente.quant_parcelas,
            }
        
        id_pessoa = self.pegar_id_pessoa(cliente.cpf)['id']
        lista_resultados = list()
        resultado = self.fila_de_venda(id_pessoa, cliente.valor_servico, 
                                        cliente.quant_parcelas, cliente.matricula)
        lista_resultados.append(resultado)

        # if cliente.decimo_terceiro:
        #     resultado = self.fila_de_venda(cliente.quant_parcelas + 1, id_pessoa, 
        #                                    cliente.valor_servico, proxima_data, cliente.matricula)
        #     lista_resultados.append(resultado)
        
        self.salvar_sucesso_csv(lista_resultados, cliente)
        return lista_resultados

    def salvar_sucesso_csv(self, resultados, cliente):
        tem_erro = any(resultado["error"] for resultado in resultados)
        if not tem_erro:
            sucesso = {
                    "cpf": cliente.cpf,
                    "matricula": cliente.matricula,
                    "valorServico": cliente.valor_servico,
                    "quantParcelas": cliente.quant_parcelas,
                    "decimoTerceiro": cliente.decimo_terceiro
                    }
            self.escrever_csv(sucesso)

    def escrever_csv(self, sucessoDic):
        df = pd.DataFrame(sucessoDic, index=[0])
        if not df.empty:
            file_exists = True
            try:
                df_existing = pd.read_csv("sucesso_criados.csv")
            except FileNotFoundError:
                file_exists = False

            if file_exists:
                df = pd.concat([df_existing, df], ignore_index=True)

            df.to_csv("sucesso_criados.csv", index=False)

    def salvar_registro_execucao(self, list_resultado, cliente):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_{timestamp}.txt"
        with open(filename, "w") as f:
            for resultado in list_resultado:
                f.write(str({cliente.cpf: resultado}) + "\n")



# auth = ContaAzulAuth()
# new_config = auth.refresh_access_token()
# auth.update_config(new_config)

# # df = pd.read_csv("CLIENTES_PISO.csv")
# venda_controller = VendaController(new_config['access_token'])
# lista_dados = list()

# dados = [{'cpf': '00910849544',
#         'matricula': 'TESTE HENRIQUE',
#         'valor_servico': int('10000'),
#         'quant_parcelas': int('2'),
#         'decimo_terceiro': False  # Adicionei essa chave, assumindo False como padrão
#     }]

# for linha in dados:
#     cliente = Cliente(**linha)
#     resultado = venda_controller.processar_cliente(cliente)
#     lista_dados.append(resultado)
#     venda_controller.processar_cliente(lista_dados, cliente)
#     # Salvar a lista de dicionários com timestamp

