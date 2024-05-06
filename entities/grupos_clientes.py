from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class GruposClientes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'grupos_clientes'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_grupos_clientes.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS grupos_clientes
            (
                grupo_cliente numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                descricao character varying(60)
            );
        """
