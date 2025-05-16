from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FornecedoresDescontosMarcas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'fornecedores_descontos_marcas'
        self.columns = [
            "fornecedor_desconto_marca",
            "formulario_origem",
            "tab_master_origem",
            "reg_master_origem",
            "reg_log_inclusao",
            "fornecedor_desconto",
            "marca",
            "percentual_desconto",
            "tipo"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_fornecedores_descontos_marcas.sql', 'r') as file:
            return file.read()