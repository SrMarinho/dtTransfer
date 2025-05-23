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
        self.name = 'f_mapear_contas_lanc_contabil'
        self.columns = [
            'grupo',
            'empresa', 
            'filial', 
            'data_lancamento', 
            'conta_reduzida', 
            'descr_conta_rdz',
            'valor', 
            'lote', 
            'origem', 
            'descr_origem', 
            'cod_custo', 
            'descr_custo', 
            'deb_cred'
        ]

    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_mapear_contas_lanc_contabil.sql', 'r') as file:
            return file.read()

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
                                A.data_lancamento::date >= '{startDate}'
                                and A.data_lancamento::date < '{endDate}'
                            """
                        )
                    conn.commit()
            logger.info(f"{self.name} - Foram deletados registro no dia {startDate} ao dia {endDate}.")
            
        except Exception as e:
            logger.info("Erro ao tentar deletar registros da tabela {} entre as datas de {} e {}.".format(self.name, startDate, endDate))
            raise e
