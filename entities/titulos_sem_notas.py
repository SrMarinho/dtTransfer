from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 


class TitulosSemNotas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'titulos_sem_notas'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_titulos_sem_notas.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.tableName} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {self.tableName} A WHERE A.data_entrada_titulo = TO_CHAR('{startDate}'::DATE, 'DD/MM/YYYY');")
                logger.info(f"{self.tableName} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.tableName} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE titulos_sem_notas (
                cod_transacao varchar(5),
                desc_transacao varchar(60),
                data_entrada_titulo varchar(10),
                empresa integer,
                filial_erp integer,
                nome_filial varchar(30),
                seq_mov integer,
                filial_linx varchar(3),
                cidade_filial varchar(60),
                uf_filial varchar(2),
                cod_cc_titulo varchar(9),
                descr_cc_rat_titulo varchar(80),
                cod_contabil_titulo numeric(38,0),
                descr_conta varchar(250),
                valo_rateio_titulo numeric(15,2),
                data_emissao_titulo varchar(10),
                nfe_titulo numeric(9,0),
                serie_nf_entrata_titulo varchar(3),
                venc_original varchar(10),
                venc_prorrogada varchar(10),
                data_pagto varchar(10),
                cod_forma_pagto integer,
                descr_forma_pagto varchar(30),
                situacao_titulo varchar(2),
                titulo varchar(15),
                tipo varchar(3),
                descr_tipo_titulo varchar(40),
                cod_forn numeric(9,0),
                nome_fornecedor varchar(100),
                nome_fantasia_forn varchar(50),
                cpnj_cpf numeric(14,0),
                irrf numeric(15,2),
                iss numeric(15,2),
                inss numeric(15,2),
                pis numeric(14,2),
                cofins numeric(14,2),
                csll numeric(15,2),
                outras_retencoes numeric(15,2),
                total_titulo numeric(15,2),
                valor_aberto_titulo numeric(15,2),
                observacao varchar(250),
                juros numeric(15,2),
                multa numeric(15,2),
                engargo numeric(15,2),
                acrescimo numeric(15,2),
                desconto numeric(15,2),
                outros_descontos numeric(15,2),
                cod_usu_apr_oc numeric(38,0),
                nome_usu_apr_oc varchar(255),
                nivel_aprovador numeric(38,0),
                tipo2 char(16),
                num_lote_contabil numeric(9,0)
            );
        """
