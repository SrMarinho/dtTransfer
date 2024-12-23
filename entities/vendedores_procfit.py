from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class VendedoresProcfit(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'vendedores_procfit'
        self.columns = [
            'codigo_vendedor', 
            'nome_vendedor',
            'tipo_vendedor',
            'codigo_supervisor',
            'cargo_comercial', 
            'cargo_comercial_descricao',
            'comissao_liquidez',
            'comissao_venda'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_vendedores_procfit.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
