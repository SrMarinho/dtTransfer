from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FornecedoresDescontos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'fornecedores_descontos'
        self.columns = [
            "fornecedor_desconto",
            "formulario_origem",
            "tab_master_origem",
            "reg_master_origem",
            "reg_log_inclusao",
            "data_hora",
            "usuario_logado",
            "fornecedor",
            "data_ini",
            "data_fim",
            "percentual_desconto",
            "processar",
            "descricao",
            "tipo_fornecedor",
            "guid",
            "ativo",
            "inativar_produtos_fora_mix",
            "marca",
            "data_validade_ini",
            "data_validade_fim"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_fornecedores_descontos.sql', 'r') as file:
            return file.read()