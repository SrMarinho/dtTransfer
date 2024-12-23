from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class MetasVendasEmpresas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'metas_vendas_empresas'
        self.columns = [
            'meta_venda_empresa',
            'meta_venda',
            'empresa',
            'meta',
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_metas_vendas_empresas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS metas_vendas_empresas
            (
                meta_venda_empresa numeric(15,0),
                meta_venda numeric(15,0),
                empresa numeric(15,0),
                meta numeric(15,2)
            );
        """
