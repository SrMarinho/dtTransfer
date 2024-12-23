from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Dcusto(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'd_custos'
        self.columns = [
            "empresa",
            "cod_custo",
            "descr_custo",
            "tipo",
            "aceita_rat",
            "data_alt",
            "tipo_custo",
            "descr_tipo_custo",
            "custo_pai"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_d_custos.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS d_custos
            (
                empresa integer,
                cod_custo character varying(9) COLLATE pg_catalog."default",
                descr_custo character varying(80) COLLATE pg_catalog."default",
                tipo character varying(1) COLLATE pg_catalog."default",
                aceita_rat character(3) COLLATE pg_catalog."default",
                data_alt character varying(10) COLLATE pg_catalog."default",
                tipo_custo integer,
                descr_tipo_custo character varying(30) COLLATE pg_catalog."default",
                custo_pai character varying(9) COLLATE pg_catalog."default"
            )
        """
