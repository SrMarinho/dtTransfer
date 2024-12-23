from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class MetasVendasVendedores(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'metas_vendas_vendedores'
        self.columns = [
            'meta_venda_vendedor',
            'meta_venda',
            'vendedor',
            'meta',
            'empresa'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_metas_vendas_vendedores.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS metas_vendas_vendedores
            (
                meta_venda_vendedor numeric(15,0),
                meta_venda numeric(15,0),
                vendedor numeric(15,0),
                meta numeric(15,2),
                empresa numeric(15,0)
            );
        """
