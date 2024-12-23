from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class WmsFollowSeparacoesDataTipoProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'wms_follow_separacoes_data_tipo_produtos'
        self.columns = [
            'pedido_venda',
            'data',
            'tipo_romaneio',
            'produto',
            'descricao',
            'empresa_origem',
            'centro_estoque_origem',
            'entidade_destino',
            'nome_entidade_destino',
            'rota',
            'rota_descricao',
            'qtde_original',
            'qtde_separacao',
            'qtde_conferencia',
            'saldo',
            'qtde_n_atendida',
            'notas',
            'checkout',
            'status_pedidos_vendas'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_wms_follow_separacoes_data_tipo_produtos.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS wms_follow_separacoes_data_tipo_produtos
            (
                pedido_venda numeric(15,0),
                data timestamp without time zone,
                tipo_romaneio character varying(255) COLLATE pg_catalog."default",
                produto numeric(15,0),
                descricao character varying(255) COLLATE pg_catalog."default",
                empresa_origem numeric(15,0),
                centro_estoque_origem numeric(15,0),
                entidade_destino numeric(15,0),
                nome_entidade_destino character varying(255) COLLATE pg_catalog."default",
                rota numeric(15,0),
                rota_descricao character varying(255) COLLATE pg_catalog."default",
                qtde_original numeric(15,2),
                qtde_separacao numeric(15,2),
                qtde_conferencia numeric(15,2),
                saldo numeric(15,2),
                qtde_n_atendida numeric(15,2),
                notas text COLLATE pg_catalog."default",
                checkout numeric(15,0),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                update_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
