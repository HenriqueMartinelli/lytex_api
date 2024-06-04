from typing import NamedTuple, List, Optional


class clienteAPi(NamedTuple):
    cpfCnpj: str
    treatmentPronoun: str
    type: str
    cpfCnpj: str
    id: str
    name: str
    cellphone: str
    createdAt: str
    email: str
    referenceId: str


class Produto(NamedTuple):
    reference_id: str
    due_date_days: int
    overdue_payment_days: int
    day: int
    next_at: str 
    unit: str
    value: int


class Cliente(NamedTuple):
    cpf: str
    matricula: str
    valorServico: int
    quantParcelas: int
    decimoTerceiro: bool
