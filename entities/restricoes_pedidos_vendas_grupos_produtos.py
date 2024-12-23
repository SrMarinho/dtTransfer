from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RestricoesPedidosVendasGruposProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'restricoes_pedidos_vendas_grupos_produtos'
        self.columns = [
            'restricao_pedido_venda_grupo_produto', 
            'restricao_pedido_venda', 
            'grupo_produto', 
            'tipo_restricao'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
