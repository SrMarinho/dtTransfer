from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class ClienteVendedor(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'cliente_vendedor'
        self.columns = [
            'cliente', 
            'empresa', 
            'vendedor'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_cliente_vendedor.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS cliente_vendedor
            (
                cliente integer NOT NULL,
                empresa integer NOT NULL,
                vendedor integer NOT NULL,
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
