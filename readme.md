# Integração Oxy com Serviço Lytex

Este documento descreve como configurar e executar a integração entre o Oxy e o serviço Lytex.

## Estrutura de Arquivos

A estrutura de arquivos deve conter uma pasta `configs` com um arquivo `config.json` com as seguintes informações:

json
{
    "accessToken": "****",
    "refreshToken": "****",
    "expireAt": "***",
    "refreshExpireAt": "***",
    "clientSecret": "***",
    "clientId": "***"
}


##  Banco de Dados

Este serviço irá precisar de um servidor MongoDB online em localhost.

    URI: mongodb://localhost:27017/
    Nome do banco: oxylytex
    Nome da coleção: boletos

Certifique-se de que o banco e a coleção mencionados existam.
## Como Rodar

    1. instale as dependências:
        pip install -r requirements.txt
    2. Execute
        python contrato.runner.py