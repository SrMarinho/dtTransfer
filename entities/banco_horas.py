from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 


class BancoHoras(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'banco_horas'
        self.columns = [
            "empresa",
            "cod_tipo",
            "descr_tipo",
            "matricula",
            "cod_banco_horas",
            "descr_banco_horas",
            "cod_situacao",
            "descr_situacao",
            "orgem_lancamento",
            "soma_diminui",
            "qtda_horas_lancamento",
            "qtda_horas_pagas",
            "qtda_horas_a_compensar",
            "data_limite_compensacao",
            "data_lancamento"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_banco_horas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS banco_horas
            (
                empresa numeric(4,0),
                cod_tipo numeric(1,0),
                descr_tipo character varying(9),
                matricula numeric(9,0),
                cod_banco_horas numeric(5,0),
                descr_banco_horas character varying(30),
                cod_situacao numeric(3,0),
                descr_situacao character varying(30),
                orgem_lancamento character varying(23),
                soma_diminui character varying(1),
                qtda_horas_lancamento character varying(13),
                qtda_horas_pagas character varying(13),
                qtda_horas_a_compensar character varying(13),
                data_limite_compensacao character varying(10),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
