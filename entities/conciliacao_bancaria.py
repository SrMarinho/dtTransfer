from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class ConciliacaoBancaria(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'conciliacao_bancaria'
        self.columns = [
            "dia",
            "mes",
            "ano",
            "vlrcreditadobanco",
            "vlrbaixado",
            "saldo",
            "hismov"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_conciliacao_bancaria.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS conciliacao_bancaria
            (
                dia numeric(38,0),
                mes numeric(38,0),
                ano numeric(38,0),
                vlrcreditadobanco numeric(38,2),
                vlrbaixado numeric(38,2),
                saldo numeric(38,2),
                hismov character varying(100),
                created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
