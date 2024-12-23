from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class AfastamentoColaboradores(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'afastamento_colaboradores'
        self.columns = [
            'data_afastamento',
            'empresa',
            'cod_filial',
            'nome_filial',
            'uf',
            'tipo',
            'nome_tipo',
            'matricula',
            'situacao',
            'desc_situacao',
            'qta_dias',
            'ciddez',
            'desc_ciddez',
            'ciddez_subgrupo',
            'desc_ciddez_subgrupo'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_afastamento_colaboradores.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM {self.name} WHERE data_afastamento::date = '{startDate}';""")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}! - {str(e)}")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.afastamento_colaboradores
            (
                empresa numeric(4,0),
                cod_filial numeric(6,0),
                nome_filial character varying(40) COLLATE pg_catalog."default",
                uf character varying(4) COLLATE pg_catalog."default",
                tipo numeric(1,0),
                nome_tipo character varying(9) COLLATE pg_catalog."default",
                matricula numeric(9,0),
                situacao numeric(3,0),
                desc_situacao character varying(30) COLLATE pg_catalog."default",
                qta_dias numeric(4,0),
                ciddez character varying(4) COLLATE pg_catalog."default",
                desc_ciddez character varying(400) COLLATE pg_catalog."default",
                ciddez_subgrupo character varying(3) COLLATE pg_catalog."default",
                desc_ciddez_subgrupo character varying(300) COLLATE pg_catalog."default",
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                data_afastamento date NOT NULL
            )
        """
