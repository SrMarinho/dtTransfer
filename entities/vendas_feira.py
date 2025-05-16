from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class VendasFeira(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'vendas_feira'
        self.columns = [
            "pedido_venda_validacao",
            "pedido_venda",
            "data_hora",
            "status",
            "origem_venda_canal",
            "total_pedido",
            "total_nf",
            "empresa",
            "vendedor",
            "vendedor_descricao",
            "entidade",
            "razao_social",
            "nome_fantasia",
            "inscricao_federal",
            "estado",
            "condicao_comercial",
            "condicao_comercial_descricao",
            "configuracao_ol",
            "configuracao_ol_descricao",
            "grupo_cliente",
            "grupo_cliente_descricao",
            "cliente_rede",
            "cliente_rede_descricao",
            "marca",
            "marca_descricao",
            "fabricante",
            "categoria"
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_vendas_feira.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e