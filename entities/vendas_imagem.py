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
            'movimento',
            'margem'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_vendas_imagem.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM {self.name} WHERE movimento::date = '{startDate}';""")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e
    
    def deleteMonth(self, startDate, endDate):
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"""
                            DELETE 
                            FROM
                                {self.name} A
                            WHERE
                                A.movimento::date >= '{startDate}'
                                and A.movimento::date < '{endDate}'
                            """
                        )
                    conn.commit()
            logger.info(f"{self.name} - Foram deletados registro no dia {startDate} ao dia {endDate}.")
            
        except Exception as e:
            logger.info("Erro ao tentar deletar registros da tabela {} entre as datas de {} e {}.".format(self.name, startDate, endDate))
            raise e
