from pymongo import MongoClient

def conectar_ao_mongodb(uri, nome_banco):
    client = MongoClient(uri)
    db = client[nome_banco]
    return db

class ClienteService:
    def __init__(self, uri='mongodb://localhost:27017/', nome_banco='oxylytex', nome_colecao='boletos'):
        self.db = conectar_ao_mongodb(uri, nome_banco)
        self.colecao = self.db[nome_colecao]
    
    def calcular_incremento_piso(self, valor_servico_str):
        try:
            valor_servico_float = float(valor_servico_str.replace(',', '.'))
            incremento_piso = valor_servico_float / 0.20
            incremento_piso_formatado = "{:.2f}".format(incremento_piso)
            int_part, dec_part = incremento_piso_formatado.split('.')
            formatted_result = f"{int_part.replace('.', ',')},{dec_part}"

            return formatted_result
        except ValueError:
            return "0"


    def salvar_sucesso_mongo(self, cliente, id=None, clienteApi=None, msg=None):
        if clienteApi:
            print(f"Matricula {cliente.matricula} - Assinatura Criada com Sucesso")
            sucessoDic = {
                "cpf": cliente.cpf,
                "matricula": cliente.matricula,
                "valorServico": cliente.valorServico,
                "quantParcelas": cliente.quantParcelas,
                "decimoTerceiro": cliente.decimoTerceiro,
                "linkCobranca": f"https://checkout-pay.lytex.com.br/fatura/{id}",
                "nome": clienteApi.name,
                "telefone": clienteApi.cellphone,
                "incrementoPiso": self.calcular_incremento_piso(cliente.valorServico),
                "error": False,
                "msg": None,
            }
        else:
            print(f"Matricula {cliente.matricula} - Erro criar Assinatura para esta matrícula")
            sucessoDic = {
                "cpf": cliente.cpf,
                "matricula": cliente.matricula,
                "error": True,
                "msg": msg
            }
        
        self.colecao.insert_one(sucessoDic)
    
    def verificar_contrato_criados(self, cliente):
        resultado = self.colecao.find_one({"matricula": cliente.matricula})
        if resultado:
            return "Matricula Já existe na coleção boletos"
        return False



