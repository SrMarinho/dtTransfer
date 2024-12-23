from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class DadosColaboradores(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'dados_colaboradores'
        self.columns = [
            'numcad', 
            'nome_filial', 
            'uf', 
            'data_admissao', 
            'duracao_contrato', 
            'cod_centrocusto', 
            'nome_centrocusto', 
            'num_local', 
            'nome_local', 
            'data_alteracao_salarial', 
            'motivo_prom_salarial', 
            'nome_motivo_prom', 
            'cargo', 
            'nome_cargo', 
            'sexo', 
            'cod_raca', 
            'nome_raca', 
            'cod_graduacao', 
            'graduacao', 
            'data_nascimento', 
            'deficiente', 
            'cod_deficiencia', 
            'tipo_deficiencia', 
            'data_demissao', 
            'causa_demissao', 
            'cod_situacao', 
            'situacao'
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
