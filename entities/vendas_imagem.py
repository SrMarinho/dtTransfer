from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class VendasImagem(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'vendas_imagem'
        self.columns = [
            'nf_faturamento_produto',
            'nf_faturamento',
            'produto',
            'prec_tipo_custo',
            'quantidade_estoque',
            'preco_nf_liquido',
            'valor_desconto_fin_unit',
            'prec_custo',
            'prec_icms_valor',
            'prec_pis_valor',
            'prec_cofins_valor',
            'prec_despesas_st_valor',
            'lucro_liquido',
            'receita_liquida',
            'margem'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_vendas_imagem.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS vendas_imagem
            (
                nf_faturamento_produto numeric(15,0),
                nf_faturamento numeric(15,0),
                produto numeric(15,0),
                prec_tipo_custo character varying(1) COLLATE pg_catalog."default",
                quantidade_estoque numeric(15,2),
                preco_nf_liquido numeric(15,2),
                valor_desconto_fin_unit numeric(15,4),
                prec_custo numeric(15,2),
                prec_icms_valor numeric(15,2),
                prec_pis_valor numeric(15,2),
                prec_cofins_valor numeric(15,2),
                prec_despesas_st_valor numeric(15,2),
                lucro_liquido numeric(15,4),
                receita_liquida numeric(15,4),
                margem numeric(15, 2),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
