from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Dcusto(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'd_custos'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_d_custos.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE d_custos (
                empresa INTEGER,
                cod_custo VARCHAR(9),
                descr_custo VARCHAR(80),
                tipo VARCHAR(1),
                aceita_rat CHAR(3),
                data_alt VARCHAR(10)
            );
        """
