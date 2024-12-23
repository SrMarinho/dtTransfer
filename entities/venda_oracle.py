from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class VendaOracle(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'venda_oracle'
        self.columns = [
            'cod_filial', 
            'uf', 
            'filial', 
            'data_solicitacao', 
            'solicitacao', 
            'tipo', 
            'descr_tipo', 
            'qtd_vagas', 
            'cod_cargo', 
            'cargo', 
            'cod_situacao', 
            'situacao_solicitacao', 
            'data_criacao_requisicao', 
            'cod_requisicao', 
            'cod_situacao_requisicao', 
            'situacao_requisicao', 
            'data_previsao', 
            'data_limite_requisicao', 
            'data_encerramento_requisicao'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
