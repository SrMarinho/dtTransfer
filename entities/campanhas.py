from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Campanhas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'campanhas'
        self.columns = ['id', 'data_inicial', 'data_final', 'campanha', 'emails', 'totais_cd', 'situacao', 'objetivo', 'tipo_participante', 'criado_por']
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_campanhas.sql', 'r') as file:
                return file.read()
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar ler o arquivo de consulta!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS campanhas
            (
                id bigint NOT NULL,
                data_inicial date,
                data_final date,
                campanha character varying(255) COLLATE pg_catalog."default",
                emails text COLLATE pg_catalog."default",
                totais_cd character varying(1) COLLATE pg_catalog."default",
                situacao character varying(1) COLLATE pg_catalog."default",
                objetivo character varying(2) COLLATE pg_catalog."default",
                tipo_participante character varying(1) COLLATE pg_catalog."default",
                criado_por text COLLATE pg_catalog."default",
                CONSTRAINT campanhas_pkey PRIMARY KEY (id)
            )
        """
