from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FMapearContasLancContabil(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'f_mapear_contas_lanc_contabil'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_mapear_contas_lanc_contabil.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.tableName} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_lancamento = TO_CHAR('{}'::DATE, 'DD/MM/YYYY');".format(self.tableName, startDate))
                logger.info(f"{self.tableName} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.tableName} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE f_mapear_contas_lanc_contabil (
                empresa INTEGER,
                filial INTEGER,
                data_lancamento VARCHAR(10),
                conta_reduzida INTEGER,
                descr_conta_rdz VARCHAR(250),
                valor NUMERIC(38,2),
                lote INTEGER,
                cod_custo VARCHAR(9),
                descr_custo VARCHAR(80),
                deb_cred VARCHAR(1)
            );
        """
