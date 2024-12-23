from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class CampanhasParticipantes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'campanhas_participantes'
        self.columns = [
            'id_campanha',             
            'subcampanha',
            'codigo_universo',
            'descricao',
            'observacao',
            'tipo_restricao',
            'tipo'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_campanhas_participantes.sql', 'r') as file:
                return file.read()
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar ler o arquivo de consulta!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS campanhas_participantes
            (
                id_campanha bigint,
                subcampanha character varying(255) COLLATE pg_catalog."default",
                codigo_universo bigint,
                descricao character varying(255) COLLATE pg_catalog."default",
                observacao character varying(255) COLLATE pg_catalog."default",
                tipo_restricao character varying(1) COLLATE pg_catalog."default",
                tipo character varying(1) COLLATE pg_catalog."default"
            )

        """
