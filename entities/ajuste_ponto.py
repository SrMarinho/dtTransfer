from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class AjustePonto(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'ajuste_ponto'
        self.columns = ['empresa', 'tipo', 'matricula', 'situacao_excecao', 'cod_situacao', 'descr_situacao', 'observacao', 'data_apuracao', 'marcacao']

    
    def getQuery(self) -> str:
        with open('sqls/consulta_ajuste_ponto.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.ajuste_ponto
            (
                empresa numeric(4,0),
                tipo numeric(1,0),
                matricula numeric(9,0),
                cod_situacao numeric(3,0),
                descr_situacao character varying(30) COLLATE pg_catalog."default",
                data_apuracao character varying(10) COLLATE pg_catalog."default",
                marcacao character varying(13) COLLATE pg_catalog."default",
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP,
                situacao_excecao character varying(1) COLLATE pg_catalog."default",
                observacao character varying(128) COLLATE pg_catalog."default"
            )
        """
