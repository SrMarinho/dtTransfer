from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FtitulosComNotasServicos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'f_titulos_com_notas_servicos'
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
            'serie_nf_entrada_titulo',
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
            'iss',
            'inss',
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
            'nfe_seq_servico',
            'servico',
            'fam_servico',
            'descr_fam_serv',
            'descr_servico',
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
        with open('sqls/consulta_f_titulos_com_notas_servicos.sql', 'r') as file:
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
            CREATE TABLE f_titulos_com_notas_servicos (
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
                cod_cc_nfe varchar(9),
                descr_cc_rat_nota varchar(80),
                cod_contabil_nfe numeric(38,0),
                descr_conta varchar(250),
                valor_rat_nfe numeric(15,2),
                data_emissao_titulo varchar(10),
                nfe_titulo numeric(9,0),
                serie_nf_entrada_titulo varchar(3),
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
                diferencial_icms numeric(38,0),
                irrf numeric(15,2),
                iss numeric(15,2),
                inss numeric(15,2),
                pis_recuperar numeric(15,2),
                cofins_recuperar numeric(15,2),
                csll numeric(15,2),
                outras_retencoes numeric(15,2),
                observacao varchar(250),
                juros numeric(15,2),
                multa numeric(15,2),
                engargo numeric(15,2),
                acrescimo numeric(15,2),
                desconto numeric(15,2),
                outros_descontos numeric(15,2),
                num_ordem_compra numeric(38,0),
                num_contrato numeric(38,0),
                data_emissao_oc varchar(10),
                nota_fiscal numeric(9,0),
                nfe_seq_servico numeric(3,0),
                servico varchar(14),
                fam_servico varchar(6),
                descr_fam_serv varchar(50),
                descr_servico varchar(250),
                cod_usu_ger_oc numeric(38,0),
                nome_ger_oc varchar(255),
                cod_usu_apr_oc numeric(38,0),
                nome_usu_apr_oc varchar(255),
                nivel_aprov_ordem_compra numeric(38,0),
                cod_usu_ger_contr numeric(38,0),
                nome_usu_ger_contr varchar(255),
                cod_usu_apr_contr numeric(38,0),
                nome_usu_apr_contr varchar(255),
                nivel_aprov_contrato numeric(38,0),
                cod_proced_oc numeric(38,0),
                procedencia_oc varchar(25),
                tipo2 char(7),
                cod_sit_oc numeric(38,0),
                situacao_oc varchar(25),
                lote_contabil_titulo numeric(38,0),
                lote_contabil_nota numeric(38,0)
            );
        """
