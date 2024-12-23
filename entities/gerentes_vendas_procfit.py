from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class GerentesVendasProcfit(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'gerentes_vendas_procfit'
        self.columns = [
            'codigo_produto', 
            'ean', 
            'dum', 
            'descricao', 
            'familia', 
            'molecula', 
            'franquia', 
            'categoria', 
            'classificacao', 
            'situacao', 
            'curva', 
            'legenda', 
            'embalagem', 
            'laboratorio_id', 
            'produto_resumo', 
            'produto_resumo_descricao', 
            'preco_monitorado', 
            'grupo_produto', 
            'subgrupo_produto'
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
