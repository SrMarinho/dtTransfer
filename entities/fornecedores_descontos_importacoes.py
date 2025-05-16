from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FornecedoresDescontosImportacoes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'fornecedores_descontos_importacoes'
        self.columns = [
            "fornecedor_desconto_imp",
            "formulario_origem",
            "tab_master_origem",
            "reg_master_origem",
            "reg_log_inclusao",
            "fornecedor_desconto",
            "codigo_barras",
            "descricao",
            "referencia",
            "desconto",
            "valor_unitario",
            "produto",
            "percentual_repasse"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_fornecedores_descontos_importacoes.sql', 'r') as file:
            return file.read()