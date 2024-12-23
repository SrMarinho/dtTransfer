from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FgtsSemRescisoes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'fgts_sem_rescisoes'
        self.columns = ["empresa", "matricula", "data_vencimento", "multa", "rescisao", "indenizacao", "total"]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_fgts_sem_rescisoes.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE fgts_sem_rescisoes (
                empresa INTEGER,
                matricula INTEGER,
                tipo_rescisao VARCHAR(21),
                data_pagamento VARCHAR(10),
                valor_fgts_recolhido NUMERIC(11,2)
            );
        """
