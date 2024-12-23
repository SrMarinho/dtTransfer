from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class PedidosCompras(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'pedidos_compras'
        self.columns = [
            'unidade', 
            'pedido_compra', 
            'entidade', 
            'data_pedido', 
            'data_entrega', 
            'cod_comprador', 
            'condicao_pagamento', 
            'tipo_pedido_compra', 
            'unidade_destino_crossdocking'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
