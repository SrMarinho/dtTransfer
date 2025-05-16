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

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM {self.name} WHERE data_hora::date = '{startDate}';""")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e