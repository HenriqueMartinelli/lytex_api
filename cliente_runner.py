import json
import pandas as pd

from datetime import datetime, timedelta

from auth.lytexAuth import LyTexAuth
from types.client_types import row_to_cliente
from modifiers.criar_cliente import LytexClient

    
def autenticar_lytex():
    auth = LyTexAuth()
    new_config = auth.obtain_token()
    auth.update_config(new_config)
    return new_config['accessToken']

def ler_dados_clientes(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo, encoding='utf-16', delimiter=',')
    dados = df.to_dict('records')
    return dados

def processar_clientes(dados, bearer_token):
    cliente_controller = LytexClient(bearer_token)
    lista_dados = []

    for linha in dados:
        try:
            endereco, cliente = row_to_cliente(linha)
            payload = cliente_controller.create_payload(endereco, cliente)
            resultado = cliente_controller.create_client(payload)
            cliente_controller = verificar_token(resultado, cliente_controller, payload)
            lista_dados.append(resultado)
        except Exception as error:
            print(error)
            lista_dados.append({
                "cpf": cliente.cpf,
                "nome": cliente.name,
                "msg": error
            })
    return lista_dados

def verificar_token(response, cliente_controller, payload):
    if response.get("message"):
        if response.get("message") == "Token expirado":
            bearer_token = autenticar_lytex()
            cliente_controller = LytexClient(bearer_token)
            cliente_controller.create_client(payload)
    return cliente_controller


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



def main():
    bearer_token = autenticar_lytex()
    dados_clientes = ler_dados_clientes("geralPessoas.csv")
    lista_dados = processar_clientes(dados_clientes, bearer_token)
    _salvar_json_log_(lista_dados)
    # Salvar a lista de dicionários com timestamp

if __name__ == "__main__":
    main()