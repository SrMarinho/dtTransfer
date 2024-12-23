from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class EstoqueUsuConsumo(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'estoque_usu_consumo'
        self.columns = [
            "data_movimentacao",
            "empresa",
            "filial",
            "descr_filial",
            "filial_dep",
            "num_requisicao",
            "produto",
            "descr_produto",
            "derivacao",
            "descr_derivacao",
            "unidade_medida",
            "quantidade",
            "familia_prod",
            "desc_familia",
            "codred",
            "descr_codred",
            "valor_rateio",
            "cod_custo",
            "descr_custo",
            "lote_contabil",
            "cod_usuario",
            "nome_usuario"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_estoque_usu_consumo.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate} ...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {self.name} A WHERE A.data_movimentacao = TO_CHAR('{startDate}'::DATE, 'DD/MM/YYYY');")
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE estoque_usu_consumo (
                data_movimentacao varchar(10),
                empresa integer,
                filial integer,
                descr_filial varchar(30),
                filial_dep integer,
                num_requisicao integer,
                produto varchar(14),
                descr_produto varchar(100),
                derivacao varchar(7),
                descr_derivacao varchar(50),
                unidade_medida varchar(3),
                quantidade numeric(14,5),
                familia_prod varchar(6),
                desc_familia varchar(50),
                codred integer,
                descr_codred varchar(250),
                valor_rateio numeric(15,2),
                cod_custo varchar(9),
                descr_custo varchar(80),
                lote_contabil integer,
                cod_usuario integer,
                nome_usuario varchar(255)
            );
        """
