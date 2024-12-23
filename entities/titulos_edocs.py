from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class TitulosEdocs(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'titulos_edocs'
        self.columns = [
            'empresa',
            'filial_erp',
            'cnpj',
            'filial_linx',
            'nome_filial',
            'cnpj_fornecedor',
            'nome_fornecedor',
            'data_emissao',
            'numero',
            'valor_nota',
            'cfop',
            'produto_erp',
            'codigo_produto_forn',
            'valor_bruto_produto',
            'desc_produto',
            'icms_st_produto',
            'ipi_produto',
            'frete_produto',
            'seguro_produto',
            'embalagem_produto',
            'encargos_produto',
            'outros_desp_produto',
            'valor_liquido_produto',
            'cod_barra_produto',
            'chave',
            'filial_nfe_entrada',
            'forn_nfe_entrada',
            'numero_nfe_entrada',
            'titulo',
            'cancelado'
        ]

    
    def getQuery(self) -> str:
        with open('sqls/consulta_titulos_edocs.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {self.name} A WHERE A.data_emissao::date = '{startDate}';")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.titulos_edocs
            (
                empresa integer,
                filial_erp integer,
                cnpj bigint,
                filial_linx character varying(3),
                nome_filial character varying(30),
                cnpj_fornecedor bigint,
                nome_fornecedor character varying(50),
                data_emissao date,
                numero integer,
                valor_nota numeric(15,2),
                cfop character varying(5),
                produto_erp character varying(14),
                codigo_produto_forn character varying(60),
                valor_bruto_produto numeric(15,2),
                desc_produto numeric(15,2),
                icms_st_produto numeric(15,2),
                ipi_produto numeric(15,2),
                frete_produto numeric(15,2),
                seguro_produto numeric(15,2),
                embalagem_produto numeric(15,2),
                encargos_produto numeric(15,2),
                outros_desp_produto numeric(15,2),
                valor_liquido_produto numeric(38,-127),
                cod_barra_produto character varying(30),
                chave character varying(50),
                filial_nfe_entrada numeric(38,-127),
                forn_nfe_entrada numeric(38,-127),
                numero_nfe_entrada numeric(38,-127),
                titulo character varying(15),
                cancelado character varying(1),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """
