from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class CampanhasEmpresas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'campanhas_empresas'
        self.columns = [
            'id_campanha',
            'meta_cnpj',
            'meta_quantidade',
            'meta_valor',
            'subcampanha',
            'empresa'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_campanhas_empresas.sql', 'r') as file:
                return file.read()
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar ler o arquivo de consulta!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS campanhas_empresas
            (
                id_campanha bigint,
                meta_cnpj bigint,
                meta_quantidade bigint,
                meta_valor double precision,
                subcampanha character varying(255) COLLATE pg_catalog."default",
                empresa bigint
            )
        """
