from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 


class Rescisoes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'rescisoes'
        self.columns = [
            "empresa",
            "matricula",
            "data_demissao",
            "cod_causa",
            "descr_causa",
            "cod_motivo",
            "descr_motivo",
            "saldo_fgts",
            "total_proventos_resc",
            "total_desconto_resc",
            "total_liq_resc",
            "data_dissidio",
            "total_proventos_resc_compl",
            "total_desconto_resc_compl",
            "total_liq_resc_dissidio"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_rescisoes.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_demissao = TO_CHAR('{}'::DATE, 'DD/MM/YYYY');".format(self.name, startDate))
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE rescisoes (
                empresa INTEGER,
                matricula INTEGER,
                data_demissao VARCHAR(10),
                cod_causa INTEGER,
                descr_causa VARCHAR(30),
                cod_motivo INTEGER,
                descr_motivo VARCHAR(40),
                saldo_fgts NUMERIC(11,2),
                total_proventos_resc NUMERIC(11,2),
                total_desconto_resc NUMERIC(11,2),
                total_liq_resc NUMERIC(38,0),
                data_dissidio VARCHAR(10),
                total_proventos_resc_compl NUMERIC(11,2),
                total_desconto_resc_compl NUMERIC(11,2),
                total_liq_resc_dissidio NUMERIC(38,0)
            );
        """
