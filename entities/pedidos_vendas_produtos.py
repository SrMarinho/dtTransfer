from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class PedidosVendasProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'pedidos_vendas_produtos'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas_produtos.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.pedidos_vendas_produtos
            (
                pedido_venda_validacao numeric(15,0),
                pedido_venda numeric(15,0),
                produto numeric(15,0),
                descricao_produto character varying(255) COLLATE pg_catalog."default",
                motivo character varying(60) COLLATE pg_catalog."default",
                valor_unitario numeric(15,2),
                desconto numeric(15,2),
                total_desconto numeric(15,2),
                quantidade_atendida numeric(15,2),
                quantidade_digitada numeric(15,2),
                valor_atendido numeric(15,2),
                valor_digitado numeric(15,2),
                condicao_pagamento numeric(15,0),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
