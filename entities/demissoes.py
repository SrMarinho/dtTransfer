from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Demissoes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'demissoes'
        self.columns = [
            'empresa', 
            'matricula', 
            'data_demissao', 
            'cod_causa', 
            'descr_causa', 
            'cod_motivo', 
            'descr_motivo', 
            'data_aviso', 
            'data_fim_aviso', 
            'dias_aviso', 
            'base_inss_saldo', 
            'base_inss_13sal', 
            'base_ir_saldo', 
            'abatim_ir_saldo', 
            'base_ir_13sal', 
            'abatim_ir_13sal', 
            'base_ir_ferias', 
            'abatim_ir_ferias', 
            'base_ir_partic_lucros', 
            'base_fgts', 
            'abatim_fgts', 
            'base_fgts_13sal', 
            'abatim_fgts_13sal', 
            'total_proventos', 
            'total_desconto', 
            'total_liquido'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_venda.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM {self.name} WHERE data_emissao::date = '{startDate}';""")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
        """
