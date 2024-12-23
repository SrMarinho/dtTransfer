from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class PedidosVendas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'pedidos_vendas'
        self.columns = [
            'pedido_venda_validacao',
            'pedido_venda',
            'nf_numero',
            'empresa',
            'data_hora',
            'data_hora_lib',
            'entidade',
            'vendedor',
            'vendedor_nome',
            'dono',
            'dono_nome',
            'condicao_comercial',
            'condicao_comercial_descricao',
            'codigo_condicao_comercial',
            'origem_venda_canal',
            'origem_venda_canal_descricao',
            'status_pedidos_vendas',
            'configuracao_ol',
            'quantidade_atendida',
            'quantidade_digitada',
            'valor_atendido',
            'valor_digitado',
            'condicao_pagamento'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS pedidos_vendas
            (
                pedido_venda_validacao numeric(15,0),
                pedido_venda numeric(15,0),
                nf_numero numeric(15,0),
                empresa numeric(15,0),
                data_hora timestamp without time zone,
                entidade numeric(15,0),
                vendedor numeric(15,0),
                vendedor_nome character varying(60) COLLATE pg_catalog."default",
                dono numeric(15,0),
                dono_nome character varying(60) COLLATE pg_catalog."default",
                condicao_comercial numeric(15,0),
                condicao_comercial_descricao character varying(60) COLLATE pg_catalog."default",
                codigo_condicao_comercial character varying(2) COLLATE pg_catalog."default",
                origem_venda_canal numeric(15,0) NOT NULL,
                origem_venda_canal_descricao character varying(60) COLLATE pg_catalog."default",
                status_pedidos_vendas character varying(60) COLLATE pg_catalog."default",
                configuracao_ol numeric(15,0),
                quantidade_atendida numeric(15,2),
                quantidade_digitada numeric(15,2),
                valor_atendido numeric(15,2),
                valor_digitado numeric(15,2),
                condicao_pagamento numeric(15,0),
                data_hora_lib timestamp without time zone,
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """
