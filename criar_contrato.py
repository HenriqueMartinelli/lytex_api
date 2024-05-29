import json
import requests
import pandas as pd
from datetime import datetime
from typing import NamedTuple
from datetime import datetime, timezone

from produto import *
from lytexAuth import LyTexAuth


class ContratoController:
    def __init__(self, bearer_token):
        self.session = requests.Session()
        self.headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {bearer_token}'
        }

    def pegar_id_pessoa(self, cpf):
        params = {
            'search': cpf,
        }
        pegar_id = self.session.get(url='https://api-pay.lytex.com.br/v2/clients', 
                                    params=params, 
                                    headers=self.headers, 
                                    timeout=20)
        if pegar_id.json().get("result") == []:
            raise ValueError("Cliente não cadastrado")
        print(pegar_id.json())
        resultado = pegar_id.json()["results"][0]
        resultado["id"] = resultado["_id"]
        resultado.pop('_id', None)
        return resultado

    def criar_contrato(self, clienteApi, cliente):
        now = datetime.now(timezone.utc)
        now_iso_format = now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

        with open("contrato.json", "r") as f:
           json_data = json.load(f)

        json_data["client"].update({
                "name": clienteApi.name,  "treatmenPronoun":clienteApi.treatmentPronoun,
                "type": clienteApi.type,  "cpfCnpj": clienteApi.cpfCnpj,
                "cellphone":clienteApi.cellphone,  "createdAt": clienteApi.createdAt,
                "email": clienteApi.email})
        
        json_data["recurrence"].update({"nextAt": now_iso_format})
        json_data["duration"].update({"value": cliente.quant_parcelas})
        json_data["items"][0].update({"value": cliente.valor_servico})

        json_data["observation"] = f"""
                Conforme contrato, o percentual de 20% é exclusivo para filiados,
                de modo que, ao pagar o boleto, concorda em ser feito o desconto
                da mensalidade da AFPEB ou ACEB🚀🚀Referente aos honorários da
                implementação do seu Piso Nacional, na Matrícula {cliente.matricula},
                sendo devida por 12 meses, com 13o.""".strip()
        self._salvar_json_log_(json_data)
        return self.session.post(url='https://api.contaazul.com/v1/contracts', 
                                headers=self.headers, 
                                json=json_data, 
                                timeout=20)


    def _serializar_dados_(self,dados):
        # Converter objetos datetime em strings
        for chave, valor in dados.items():
            if isinstance(valor, datetime):
                dados[chave] = valor.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(valor, ValueError):
                dados[chave] = str(valor)
        return dados

    def objeto_nao_serializavel(self, obj):
        if isinstance(obj, (datetime, Exception)):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _salvar_json_log_(self, lista_dados, nome_arquivo=None):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"teste.json"

            # Serializar cada elemento da lista
            # lista_serializada = [self._serializar_dados_(dado) for dado in lista_dados]

            with open(nome_arquivo, "w") as arquivo:
                json.dump(lista_dados, arquivo, indent=4)

            print(f"Arquivo JSON salvo com sucesso: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o log: {str(e)}")

    def processar_cliente(self, cliente):
        if cliente.quant_parcelas > 48:
            return {
            "error": False,
            "numeroParcela": cliente.quant_parcelas,
            "msg": "Parcelas não podem ser superior a 48"
            }
        try:
            pessoa_json = self.pegar_id_pessoa(cliente.cpf)
            cliente_api= clienteAPi(**pessoa_json)
            resultado = self.criar_contrato(cliente_api, cliente)
            print(resultado)
            # self.salvar_sucesso_csv(cliente)

        except Exception as erro:
            resultado = {
                "cpf": cliente.cpf,
                "matricula": cliente.matricula,
                "msg": erro.args[0]
            }
        print(resultado)
        return resultado

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

    def escrever_csv(self, cliente):
        sucessoDic = {"cpf": cliente.cpf, "valorServico": cliente.valor_servico,
         "quantParcelas": cliente.quant_parcelas, "decimoTerceiro": cliente.decimo_terceiro}
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

    def _serializar_dados_(self, dados):
        # Converter objetos datetime em strings
        for chave, valor in dados.items():
            if isinstance(valor, datetime):
                dados[chave] = valor.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(valor, ValueError):
                dados[chave] = str(valor)
        return dados

    def objeto_nao_serializavel(self, obj):
        if isinstance(obj, (datetime, Exception)):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _salvar_json_log_(self, lista_dados, nome_arquivo=None):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"resultados_{timestamp}.json"

            # Serializar cada elemento da lista
            lista_serializada = [self._serializar_dados_(dado) for dado in lista_dados]

            with open(nome_arquivo, "w") as arquivo:
                json.dump(lista_serializada, arquivo, indent=4, default=self.objeto_nao_serializavel)

            print(f"Arquivo JSON salvo com sucesso: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o log: {str(e)}")
    





# # df = pd.read_csv("CLIENTES_PISO.csv")
# venda_controller = VendaController(new_config['access_token'])
# lista_dados = list()
