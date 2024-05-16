from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FTitulosComNotasProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'f_titulos_com_notas_produtos'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_titulos_com_notas_produtos.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"Apagando registros no dia {startDate} na tabela {self.tableName}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_entrada_titulo = TO_CHAR('{}'::DATE, 'DD/MM/YYYY');".format(self.tableName, startDate))
                logger.info(f"Registros apagados com sucesso no dia {startDate} na tabela {self.tableName}!")
        except Exception as e:
            logger.info(f"Erro ao tentar apagar registros no dia {startDate} na tabela {self.tableName}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE f_titulos_com_notas_produtos (
                cod_transacao VARCHAR(5),
                desc_transacao VARCHAR(60),
                data_entrada_titulo VARCHAR(10),
                empresa INTEGER,
                filial_erp INTEGER,
                nome_filial VARCHAR(30),
                seq_mov INTEGER,
                filial_linx VARCHAR(3),
                cidade_filial VARCHAR(60),
                uf_filial VARCHAR(2),
                cod_cc_nfe VARCHAR(9),
                descr_cc_rat_nota VARCHAR(80),
                cod_contabil_nfe NUMERIC(38,0),
                descr_conta VARCHAR(250),
                valor_rat_nfe NUMERIC(15,2),
                data_emissao_titulo VARCHAR(10),
                nfe_titulo NUMERIC(9,0),
                serie_nf_entrata_titulo VARCHAR(3),
                venc_original VARCHAR(10),
                venc_prorrogada VARCHAR(10),
                data_pagto VARCHAR(10),
                cod_forma_pagto INTEGER,
                descr_forma_pagto VARCHAR(30),
                situacao_titulo VARCHAR(2),
                titulo VARCHAR(15),
                tipo VARCHAR(3),
                descr_tipo_titulo VARCHAR(40),
                cod_forn NUMERIC(9,0),
                nome_fornecedor VARCHAR(100),
                nome_fantasia_forn VARCHAR(50),
                cpnj_cpf NUMERIC(14,0),
                diferencial_icms NUMERIC(38,0),
                irrf NUMERIC(15,2),
                pis_recuperar NUMERIC(15,2),
                cofins_recuperar NUMERIC(15,2),
                csll NUMERIC(15,2),
                outras_retencoes NUMERIC(15,2),
                observacao VARCHAR(250),
                juros NUMERIC(15,2),
                multa NUMERIC(15,2),
                engargo NUMERIC(15,2),
                acrescimo NUMERIC(15,2),
                desconto NUMERIC(15,2),
                outros_descontos NUMERIC(15,2),
                num_ordem_compra NUMERIC(38,0),
                num_contrato NUMERIC(38,0),
                data_emissao_oc VARCHAR(10),
                nota_fiscal NUMERIC(9,0),
                nfe_seq_produto NUMERIC(3,0),
                produto VARCHAR(14),
                fam_produto VARCHAR(6),
                descr_fam_prod VARCHAR(50),
                descr_produto VARCHAR(250),
                cod_usu_ger_oc NUMERIC(38,0),
                nome_ger_oc VARCHAR(255),
                cod_usu_apr_oc NUMERIC(38,0),
                nome_usu_apr_oc VARCHAR(255),
                nivel_aprov_ordem_compra NUMERIC(38,0),
                cod_usu_ger_contr NUMERIC(38,0),
                nome_usu_ger_contr VARCHAR(255),
                cod_usu_apr_contr NUMERIC(38,0),
                nome_usu_apr_contr VARCHAR(255),
                nivel_aprov_contrato NUMERIC(38,0),
                cod_proced_oc NUMERIC(38,0),
                procedencia_oc VARCHAR(25),
                tipo2 CHAR(7),
                cod_sit_oc NUMERIC(38,0),
                situacao_oc VARCHAR(25),
                lote_contabil_titulo NUMERIC(38,0),
                lote_contabil_nota NUMERIC(38,0)
            );
        """
