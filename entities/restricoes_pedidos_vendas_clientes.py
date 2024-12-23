from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RestricoesPedidosVendasClientes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'restricoes_pedidos_vendas_clientes'
        self.columns = [
            'restricao_pedido_venda_cliente', 
            'restricao_pedido_venda', 
            'codigo_cliente', 
            'codigo_grupo', 
            'codigo_rede', 
            'tipo_restricao', 
            'descricao', 
            'empresa'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
