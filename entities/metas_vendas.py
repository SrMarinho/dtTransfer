from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class MetasVendas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'metas_vendas'
        self.columns = [
            'meta_venda',
            'data_hora',
            'ano',
            'mes',
            'descricao',
            'empresa'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_metas_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS metas_vendas
            (
                meta_venda numeric(15,0),
                data_hora timestamp without time zone,
                ano numeric(4,0),
                mes numeric(2,0),
                descricao character varying(60),
                empresa numeric(15,0)
            );
        """
