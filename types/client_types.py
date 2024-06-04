import pandas as pd
from typing import NamedTuple

class Address(NamedTuple):
    street: str  # Endereço
    zone: str    # Bairro
    city: str    # Cidade
    state: str   # Estado
    number: str  # Número
    complement: str  # Complemento
    zip: str  # CEP

class Cliente(NamedTuple):
    client_code: str  # Código do Cliente
    name: str  # Nome do cliente / Nome Fantasia *
    legal_name: str  # Razão Social
    cnpj: str  # CNPJ
    optante_simples: str  # Optante pelo SIMPLES
    inscricao_estadual: str  # Inscrição Estadual
    indicador_ie: str  # Indicador de inscrição estadual
    inscricao_suframa: str  # Inscrição Suframa
    inscricao_municipal: str  # Inscrição Municipal
    cpf: str  # CPF
    rg: str  # RG
    birth_date: str  # Data de nascimento / Fundação
    email: str  # Email
    address: Address  # Endereço completo (usando Address)
    telefone: str  # Telefone
    cellphone: str  # Celular
    contact: str  # Contato
    observations: str  # Observações


def row_to_cliente(row):
    address = Address(
        street=row['Endereço'],
        zone=row['Bairro'],
        city=row['Cidade'],
        state=row['Estado'],
        number=row['Número'],
        complement=str(row['Complemento']).replace("nan", ""),
        zip=str(row['CEP']).split(".")[0].replace("-", "")
    )

    cliente = Cliente(
        client_code=str(row['Código do Cliente']),
        name=row['Nome do cliente / Nome Fantasia *'],
        legal_name=row['Razão Social'],
        cnpj=row['CNPJ'],
        optante_simples=row['Optante pelo SIMPLES'],
        inscricao_estadual=row['Inscrição Estadual'],
        indicador_ie=row['Indicador de inscrição estadual'],
        inscricao_suframa=row['Inscrição Suframa'],
        inscricao_municipal=row['Inscrição Municipal'],
        cpf=row['CPF'].replace(".", '').replace("-", ''),
        rg=row['RG'],
        birth_date=row['Data de nascimento / Fundação'],
        email=row['Email'],
        address=address,
        telefone=row['Telefone'],
        cellphone=row['Celular'].replace(" ", ""),
        contact=row['Contato'],
        observations=row['Observações']
    )

    return address, cliente


def estado_para_sigla(nome_estado):
    estados = {
        "Acre": "AC",
        "Alagoas": "AL",
        "Amapá": "AP",
        "Amazonas": "AM",
        "Bahia": "BA",
        "Ceará": "CE",
        "Distrito Federal": "DF",
        "Espírito Santo": "ES",
        "Goiás": "GO",
        "Maranhão": "MA",
        "Mato Grosso": "MT",
        "Mato Grosso do Sul": "MS",
        "Minas Gerais": "MG",
        "Pará": "PA",
        "Paraíba": "PB",
        "Paraná": "PR",
        "Pernambuco": "PE",
        "Piauí": "PI",
        "Rio de Janeiro": "RJ",
        "Rio Grande do Norte": "RN",
        "Rio Grande do Sul": "RS",
        "Rondônia": "RO",
        "Roraima": "RR",
        "Santa Catarina": "SC",
        "São Paulo": "SP",
        "Sergipe": "SE",
        "Tocantins": "TO"
    }
    nome_estado = nome_estado.capitalize()
    if nome_estado in estados:
        return estados[nome_estado]
    else:
        raise ValueError("Estado não encontrado")
