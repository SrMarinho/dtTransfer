from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class NfCompraProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'nf_compra_produtos'
        self.columns = [
            'nf_compra_produto', 
            'nf_compra', 'referencia', 
            'produto', 
            'ean', 
            'unidade_medida', 
            'operacao_fiscal', 
            'quantidade', 
            'quantidade_embalagem', 
            'quantidade_multiplo', 
            'valor_unitario', 
            'valor_desconto', 
            'data_fabricacao', 
            'data_validade', 
            'lote', 
            'data_fabric_digitado', 
            'data_valid_digitado', 
            'valor_repasse'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_nf_compra_produtos.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.nf_compra_produtos
            (
                nf_compra_produto bigint,
                nf_compra numeric(15,0),
                referencia character varying(20) COLLATE pg_catalog."default",
                produto numeric(15,0),
                ean character varying(15) COLLATE pg_catalog."default",
                unidade_medida character varying(3) COLLATE pg_catalog."default",
                operacao_fiscal numeric(5,0),
                quantidade numeric(15,4),
                quantidade_embalagem numeric(15,4),
                quantidade_multiplo numeric(18,10),
                valor_unitario numeric(15,10),
                valor_desconto numeric(10,4),
                data_fabricacao date,
                data_validade date,
                lote character varying(20) COLLATE pg_catalog."default",
                data_fabric_digitado date,
                data_valid_digitado character varying(7) COLLATE pg_catalog."default",
                valor_repasse numeric(15,2)
            )
        """
