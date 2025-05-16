from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RecebimentoVolumesNf(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'recebimentos_volumes_nf'
        self.columns = [
            "recebimento_nf",
            "recebimento",
            "chave_nfe",
            "entidade",
            "nf_compra",
            "nf_numero",
            "nf_serie",
            "total_geral",
            "inscricao_federal",
            "volumes",
            "status_volume",
            "emissao",
            "nf_faturamento",
            "tipo_nf",
            "registro_nf"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_recebimentos_volumes_nf.sql', 'r') as file:
            return file.read()
    
    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM {self.name} WHERE emissao::date = '{startDate}';""")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def deleteMonth(self, startDate, endDate):
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""
                            DELETE 
                            FROM
                                {self.name} A
                            WHERE
                                A.emissao::date >= '{startDate}'
                                and A.emissao::date < '{endDate}'
                            """
                        )
                    conn.commit()
            logger.info(f"{self.name} - Foram deletados registros no dia {startDate} ao dia {endDate}.")
            
        except Exception as e:
            logger.info("Erro ao tentar deletar registros da tabela {} entre as datas de {} e {}.".format(self.name, startDate, endDate))
            raise e

    def createTable(self):
        creationQuery = """
        """
