from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class PaletesAlocacoes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'paletes_alocacoes'
        self.columns = [
            'palete_barras', 
            'data_hora', 
            'codigo_localizador', 
            'alocar_piking', 
            'recebimento_lancamento', 
            'centro_estoque', 
            'palete_alocacao_coletor', 
            'recebimento', 
            'tarefa', 
            'quantidade', 
            'produto', 
            'lote_validade', 
            'cracha'
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