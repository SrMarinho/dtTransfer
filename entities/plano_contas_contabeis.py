from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class PlanoContasContabeis(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'plano_contas_contabeis'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_plano_contas_contabeis.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE plano_contas_contabeis (
                empresa INTEGER,
                red INTEGER,
                descricao VARCHAR(250),
                mascara VARCHAR(40),
                classificacao VARCHAR(30),
                tipo VARCHAR(12),
                natureza VARCHAR(1)
            );
        """
