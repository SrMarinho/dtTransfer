from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RestricoesPedidosVendas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'restricoes_pedidos_vendas'
        self.columns = [
            'restricao_pedido_venda', 
            'data_hora', 
            'descricao', 
            'pedido_venda_parametro_entidade', 
            'observacao', 
            'movimento_inicial', 
            'movimento_final'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
