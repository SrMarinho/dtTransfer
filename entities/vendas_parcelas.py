from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class VendasParcelas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'vendas_parcelas'
        self.columns = [
            'venda_parcela', 
            'registro_procfit', 
            'dias', 
            'vencimento', 
            'percentual', 
            'valor', 
            'titulo'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
