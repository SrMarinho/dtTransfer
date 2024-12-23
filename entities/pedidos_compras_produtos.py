from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class PedidosComprasProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'pedidos_compras_produtos'
        self.columns = [
            'pedido_compra', 
            'referencia', 
            'produto', 
            'ean', 
            'quantidade', 
            'unidade_medida', 
            'operacao_fiscal', 
            'valor_unitario', 
            'tipo_desconto', 
            'desconto', 
            'preco_fabrica', 
            'preco_venda', 
            'preco_maximo', 
            'valor_repasse', 
            'estado'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_compras_produtos.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS pedidos_compras_produtos
            (
                pedido_compra integer,
                referencia character varying(20),
                produto integer,
                ean character varying(13),
                quantidade numeric(15,0),
                unidade_medida character varying(5),
                operacao_fiscal numeric(5,0),
                valor_unitario numeric(20,5),
                tipo_desconto character varying(1),
                desconto numeric(5,2),
                preco_fabrica numeric(20,5),
                preco_venda numeric(20,5),
                preco_maximo numeric(20,5),
                valor_repasse numeric(20,5),
                estado character varying(16),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """
