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
        self.name = 'f_titulos_com_notas_produtos'
        self.columns = [
            'cod_transacao',
            'desc_transacao',
            'data_entrada_titulo',
            'empresa',
            'filial_erp',
            'nome_filial',
            'seq_mov',
            'filial_linx',
            'cidade_filial',
            'uf_filial',
            'cod_cc_nfe',
            'descr_cc_rat_nota',
            'cod_contabil_nfe',
            'descr_conta',
            'valor_rat_nfe',
            'data_emissao_titulo',
            'nfe_titulo',
            'serie_nf_entrata_titulo',
            'venc_original',
            'venc_prorrogada',
            'data_pagto',
            'cod_forma_pagto',
            'descr_forma_pagto',
            'situacao_titulo',
            'titulo',
            'tipo',
            'descr_tipo_titulo',
            'cod_forn',
            'nome_fornecedor',
            'nome_fantasia_forn',
            'cpnj_cpf',
            'diferencial_icms',
            'irrf',
            'pis_recuperar',
            'cofins_recuperar',
            'csll',
            'outras_retencoes',
            'observacao',
            'juros',
            'multa',
            'engargo',
            'acrescimo',
            'desconto',
            'outros_descontos',
            'num_ordem_compra',
            'num_contrato',
            'data_emissao_oc',
            'nota_fiscal',
            'nfe_seq_produto',
            'produto',
            'fam_produto',
            'descr_fam_prod',
            'descr_produto',
            'cod_usu_ger_oc',
            'nome_ger_oc',
            'cod_usu_apr_oc',
            'nome_usu_apr_oc',
            'nivel_aprov_ordem_compra',
            'cod_usu_ger_contr',
            'nome_usu_ger_contr',
            'cod_usu_apr_contr',
            'nome_usu_apr_contr',
            'nivel_aprov_contrato',
            'cod_proced_oc',
            'procedencia_oc',
            'tipo2',
            'cod_sit_oc',
            'situacao_oc',
            'lote_contabil_titulo',
            'lote_contabil_nota'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_titulos_com_notas_produtos.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_entrada_titulo = TO_CHAR('{}'::DATE, 'DD/MM/YYYY');".format(self.name, startDate))
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
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
