from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Venda(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'venda'
        self.columns = [
            "codigo_cliente",
            "cnpj",
            "codigo_produto",
            "ean",
            "valor_bruto",
            "valor_liquido",
            "unidade_vendida",
            "data_emissao",
            "nota_fiscal",
            "unidade",
            "bonificacao",
            "tipo_nota",
            "registro_procfit",
            "desconto",
            "repasse",
            "suframa",
            "desconto_financeiro",
            "desconto_arquivo",
            "desconto_industria",
            "desconto_distribuidora",
            "desconto_industria_excecao",
            "desconto_distribuidora_excecao",
            "tipo_acao_desconto"
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_venda.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM {self.name} WHERE data_emissao::date = '{startDate}';""")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS venda
            (
                codigo_cliente integer,
                cnpj character varying(191),
                codigo_produto integer,
                ean character varying(191),
                valor_bruto double precision NOT NULL,
                valor_liquido double precision NOT NULL,
                unidade_vendida integer NOT NULL,
                data_emissao timestamp(0) without time zone,
                nota_fiscal integer,
                unidade integer,
                bonificacao character varying(1) COLLATE pg_catalog."default",
                tipo_nota integer,
                registro_procfit numeric(15,0),
                desconto double precision DEFAULT 0,
                repasse double precision DEFAULT 0,
                suframa double precision DEFAULT 0,
                desconto_financeiro double precision DEFAULT 0,
                desconto_arquivo double precision DEFAULT 0,
                desconto_industria double precision DEFAULT 0,
                desconto_distribuidora double precision DEFAULT 0,
                desconto_industria_excecao double precision DEFAULT 0,
                desconto_distribuidora_excecao double precision DEFAULT 0,
                tipo_acao_desconto numeric(5,0),
                created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """
