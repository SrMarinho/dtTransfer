from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FfolhaVisaoContabil(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'f_folha_visao_contabil'
        self.columns = [
            "empresa",
            "filial",
            "nome_filial",
            "data_lancamento",
            "cod_opcao_contabilidade",
            "opcao_contabilidade",
            "cod_historico",
            "valor",
            "cod_custo",
            "descr_custo",
            "codred_debito",
            "codred_credito",
            "lig_contabil",
            "descr_cod_lig_conta_contabil",
            "debcre",
            "lote_contabil"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_folha_visao_contabil.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_lancamento = TO_CHAR('{}'::DATE, 'DD/MM/YYYY');".format(self.name, startDate))
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS f_folha_visao_contabil
            (
                empresa integer,
                filial integer,
                nome_filial character varying(40),
                data_lancamento character varying(10),
                cod_opcao_contabilidade integer,
                opcao_contabilidade character varying(24),
                cod_historico integer,
                valor numeric(14,2),
                cod_custo character varying(18),
                descr_custo character varying(80),
                codred_debito integer,
                codred_credito integer,
                descr_cod_lig_conta_contabil character varying(100),
                debcre character varying(1),
                lote_contabil integer
            );
        """
