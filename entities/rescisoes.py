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
        self.tableName = 'rescisoes'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_rescisoes.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.tableName} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_demissao = TO_CHAR('{}'::DATE, 'DD/MM/YYYY');".format(self.tableName, startDate))
                logger.info(f"{self.tableName} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.tableName} - Erro ao tentar apagar registros no dia {startDate}!")
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
