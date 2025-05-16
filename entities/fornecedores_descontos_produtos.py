from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FornecedoresDescontosProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'fornecedores_descontos_produtos'
        self.columns = [
            "fornecedor_desconto_produto",
            "formulario_origem",
            "tab_master_origem",
            "reg_master_origem",
            "reg_log_inclusao",
            "fornecedor_desconto",
            "produto",
            "percentual_desconto",
            "tipo",
            "valor_unitario",
            "referencia",
            "sugestao_compra",
            "ean",
            "quantidade_minima",
            "percentual_repasse"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_fornecedores_descontos_produtos.sql', 'r') as file:
            return file.read()