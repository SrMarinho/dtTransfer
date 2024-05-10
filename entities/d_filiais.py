from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Dfiliais(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'd_filiais'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_d_filiais.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE d_filiais (
                empresa INTEGER,
                filial INTEGER,
                nome_fantasia VARCHAR(30),
                uf VARCHAR(2),
                cidade VARCHAR(60),
                cod_fil_sis_origem VARCHAR(3)
            );
        """
