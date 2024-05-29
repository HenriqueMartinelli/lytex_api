import json
import pandas as pd

from datetime import datetime, timedelta

from lytexAuth import LyTexAuth
from tipos import row_to_cliente
from criar_contrato import ContratoController
from produto import *

    
def autenticar_lytex():
    auth = LyTexAuth()
    new_config = auth.obtain_token()
    auth.update_config(new_config)
    return new_config['accessToken']

def ler_dados_clientes(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, encoding='utf-16', delimiter=',')
    dados = df.to_dict('records')
    return dados


def processar_cliente(cliente, bearer_token):
    contrato_controler = ContratoController(bearer_token)

    if cliente.quant_parcelas > 48:
        return {
        "error": False,
        "numeroParcela": cliente.quant_parcelas,
        "msg": "Parcelas não podem ser superior a 48"
        }
    try:
        pessoa_json = contrato_controler.pegar_id_pessoa(cliente.cpf)
        cliente_api= clienteAPi(**pessoa_json)
        resultado = contrato_controler.criar_contrato(cliente_api, cliente)
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

def verificar_token(response, contrato_controler, payload):
    if response.get("message"):
        if response.get("message") == "Token expirado":
            bearer_token = autenticar_lytex()
            contrato_controler = ContratoController(bearer_token)
            contrato_controler.create_client(payload)
    return contrato_controler


def _serializar_dados_(dados):
    # Converter objetos datetime em strings
    for chave, valor in dados.items():
        if isinstance(valor, datetime):
            dados[chave] = valor.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(valor, ValueError):
            dados[chave] = str(valor)
    return dados

def objeto_nao_serializavel(obj):
    if isinstance(obj, (datetime, Exception)):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _salvar_json_log_(lista_dados, nome_arquivo=None):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"resultados_{timestamp}.json"

        # Serializar cada elemento da lista
        lista_serializada = [_serializar_dados_(dado) for dado in lista_dados]

        with open(nome_arquivo, "w") as arquivo:
            json.dump(lista_serializada, arquivo, indent=4, default=objeto_nao_serializavel)

        print(f"Arquivo JSON salvo com sucesso: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar o log: {str(e)}")


def verificar_contrato_criados(cliente):
    try:
        df = pd.read_csv("sucesso_criados.csv")
        if cliente.cpf in df['cpf'].values:
            return {
            "cpf": cliente.cpf,
            "matricula": cliente.matricula,
            "msg": "Cpf Já existe na planilha sucesso_criados.csv"
        }
        return False
    except FileNotFoundError:
        return False


def main():
    dados = [{'cpf': '00910849544',
        'matricula': 'TESTE HENRIQUE',
        'valor_servico': int('10000'),
        'quant_parcelas': int('2'),
        'decimo_terceiro': False  # Adicionei essa chave, assumindo False como padrão
    }]
    bearer_token = autenticar_lytex()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"resultados_{timestamp}.json"
    with open(nome_arquivo, "w") as file:
        lista_dados = []
        for linha in dados:
            
            cliente = Cliente(**linha)
            event = verificar_contrato_criados(cliente.cpf)
            if event:
                lista_dados.append(event)
                continue
            resultado = processar_cliente(cliente, bearer_token)
            lista_dados.append(resultado)
            
            json.dump(lista_dados, file)
            file.write('\n')    
    # Salvar a lista de dicionários com timestamp

if __name__ == "__main__":
    main()



