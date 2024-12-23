from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.logger.logging import logger


class WmsFollowTemposCheckout(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'wms_follow_tempos_checkout'
        self.columns = [
            'checkout', 
            'operador', 
            'nome', 
            'embalagem_separacao', 
            'emp_cd', 
            'separado', 
            'volumes', 
            'menor_data_hora_ini_separacao', 
            'maior_data_hora_fim_separacao'
        ]
    
    def getQuery(self) -> str:
        logger.info(f"{self.name} - Lendo query...")
        try:
            with open('sqls/consulta_wms_follow_tempos_checkout.sql', 'r') as file:
                return file.read()
        except Exception as e:
            logger.info(f"{self.name} - Erro ao ler query da tabela!")
            return None

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS wms_follow_tempos_checkout
            (
                checkout numeric(15,0),
                operador numeric(15,0),
                nome character varying(60) COLLATE pg_catalog."default",
                embalagem_separacao character varying(20) COLLATE pg_catalog."default",
                emp_cd numeric(15,0),
                separado numeric(15,0),
                volumes numeric(15,0),
                menor_data_hora_ini_separacao timestamp without time zone,
                maior_data_hora_fim_separacao timestamp without time zone,
                created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
