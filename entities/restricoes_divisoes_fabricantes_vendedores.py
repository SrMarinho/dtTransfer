from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RestricoesDivisoesFabricantesVendedores(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'restricoes_divisoes_fabricantes_vendedores'
        self.columns = [
            'restricao_divisao_fabricante_vendedor', 
            'restricao_divisao_fabricante', 
            'vendedor', 
            'tipo_restricao', 
            'empresa'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
