from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class AcompanhamentoOrcamentoCompras(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'acompanhamento_orcamento_compras'
        self.columns = [
            "id",
            "mes",
            "ano",
            "comprador",
            "comprador_nome",
            "grupo_compra",
            "grupo_compra_descricao",
            "valor_orcamento",
            "valor_limite_extra",
            "total_orcamento",
            "total_compra_pedidos_original",
            "total_compras",
            "total_entrada_pedidos",
            "total_entrada_outros_pedidos",
            "p_meta",
            "saldo_compras_original",
            "saldo_compras",
            "total_entrada_geral"
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_acompanhamento_orcamento_compras.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def deleteMonth(self, startDate, endDate):
        try:
            if (self.existsTable()):
                conn = self.toDriver.connection()
                cursor = conn.cursor()
                cursor.execute(f"""
                               DELETE 
                               FROM
                                {self.name} A
                               WHERE
                                A.ano = extract(year from '{startDate}'::date)
                                AND A.mes = extract(month from '{startDate}'::date);
                               """)

                conn.commit()
                cursor.close()
                conn.close()
                logger.info(f"{self.name} - Foram deletados {cursor.rowcount} registro no dia {startDate} ao dia {endDate}.")
            else:
                logger.info("{self.name} - Tabela não existe!")
            
        except Exception as e:
            logger.info("Erro ao tentar deletar registros da tabela {} entre as datas de {} e {}.".format(self.name, startDate, endDate))
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS acompanhamento_orcamento_compras
            (
                id integer,
                mes integer,
                ano integer,
                comprador integer,
                comprador_nome character varying(60) COLLATE pg_catalog."default",
                grupo_compra integer,
                grupo_compra_descricao character varying(60) COLLATE pg_catalog."default",
                valor_orcamento numeric(40,2),
                valor_limite_extra numeric(40,2),
                total_orcamento numeric(40,2),
                total_compra_pedidos_original numeric(40,4),
                total_compras numeric(40,4),
                total_entrada_pedidos numeric(40,2),
                total_entrada_outros_pedidos integer,
                p_meta numeric(40,6),
                saldo_compras_original numeric(40,2),
                saldo_compras numeric(40,2),
                total_entrada_geral numeric(40,2),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
