import json
import pandas as pd
from datetime import datetime

from auth.lytexAuth import LyTexAuth
from configs.mongodb import ClienteService
from modifiers.criar_contrato import ContratoController
from types.contract_types import *

class ClienteProcessor:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.bearer_token = self.autenticar_lytex()
        self.mongodb = ClienteService()

    def autenticar_lytex(self):
        auth = LyTexAuth()
        new_config = auth.obtain_token()
        auth.update_config(new_config)
        return new_config['accessToken']

    def ler_dados_clientes(self):
        df = pd.read_csv(self.caminho_arquivo, encoding='utf-8', delimiter=',')
        dados = df.to_dict('records')
        return dados

    def processar_cliente(self, cliente):
        contrato_controller = ContratoController(self.bearer_token)
        id = "id não encontrado"

        if cliente.quantParcelas > 48:
            return {
                "error": True,
                "numeroParcela": cliente.quantParcelas,
                "msg": "Parcelas não podem ser superiores a 48"
            }

        try:
            pessoa_json = contrato_controller.pegar_id_pessoa(cliente.cpf)
            contrato_controller = self.verificar_token(pessoa_json, contrato_controller, cliente)
            cliente_api = clienteAPi(**pessoa_json)

            resultado = contrato_controller.criar_contrato(cliente_api, cliente)
            if resultado.get("lastInvoice"):
                id = resultado.get("lastInvoice").get("_invoiceId")

            contrato_controller = self.verificar_token(resultado, contrato_controller, cliente)
            self.mongodb.salvar_sucesso_mongo(cliente, id, cliente_api)
            return resultado

        except Exception as erro:
            self.mongodb.salvar_sucesso_mongo(cliente, msg=str(erro))
            return {
                "cpf": cliente.cpf,
                "matricula": cliente.matricula,
                "msg": str(erro)
            }

    def verificar_token(self, response, contrato_controller, cliente):
        if response.get("message"):
            if response.get("message") == "Token expirado":
                self.bearer_token = self.autenticar_lytex()
                return ContratoController(self.bearer_token)
        return contrato_controller


    def gerar_nome_arquivo(self):
        timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
        return f"outputs/resultados_{timestamp}.json"

    def processar_dados(self):
        dados = self.ler_dados_clientes()
        nome_arquivo = self.gerar_nome_arquivo()
        resultados = []
        with open(nome_arquivo, "w") as file:
            for linha in dados:
                cliente = Cliente(**linha)
                event = self.mongodb.verificar_contrato_criados(cliente)
                if event:
                    json.dump(event, file)
                    file.write('\n')
                else:
                    resultado = self.processar_cliente(cliente)
                    json.dump(resultado, file)
                    file.write('\n')
        return resultados

    def escrever_resultados(self, nome_arquivo, resultados):
        with open(nome_arquivo, "w") as file:
            for resultado in resultados:
                json.dump(resultado, file)
                file.write('\n')

    def main(self):
        self.processar_dados()

if __name__ == "__main__":
    processor = ClienteProcessor("clientesCobranca.csv")
    processor.main()
