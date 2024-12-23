from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class TitulosComNotas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'titulos_com_notas'
        self.columns = [
            "cod_transacao",
            "desc_transacao",
            "data_entrada_titulo",
            "empresa",
            "filial_erp",
            "nome_filial",
            "seq_mov",
            "filial_linx",
            "cidade_filial",
            "uf_filial",
            "cod_cc_nfe",
            "descr_cc_rat_nota",
            "cod_contabil_nfe",
            "descr_conta",
            "valor_rat_nfe",
            "data_emissao_titulo",
            "nfe_titulo",
            "serie_nf_entrada_titulo",
            "venc_original",
            "venc_prorrogada",
            "data_pagto",
            "cod_forma_pagto",
            "descr_forma_pagto",
            "situacao_titulo",
            "titulo",
            "cod_tipo",
            "descr_tipo_titulo",
            "cod_forn",
            "nome_fornecedor",
            "nome_fantasia_forn",
            "cpnj_cpf",
            "diferencial_icms",
            "irrf",
            "pis_recuperar",
            "cofins_recuperar",
            "csll",
            "outras_retencoes",
            "observacao",
            "juros",
            "multa",
            "engargo",
            "acrescimo",
            "desconto",
            "outros_descontos",
            "num_ordem_compra",
            "num_contrato",
            "data_emissao_oc",
            "nota_fiscal",
            "nfe_seq_produto",
            "produto",
            "fam_produto",
            "descr_fam_prod",
            "descr_produto",
            "cod_usu_ger_oc",
            "nome_ger_oc",
            "cod_usu_apr_oc",
            "nome_usu_apr_oc",
            "nivel_aprov_ordem_compra",
            "cod_usu_ger_contr",
            "nome_usu_ger_contr",
            "cod_usu_apr_contr",
            "nome_usu_apr_contr",
            "nivel_aprov_contrato",
            "cod_proced_oc",
            "procedencia_oc",
            "tipo",
            "cod_sit_oc",
            "situacao_oc"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_titulos_com_notas.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            if (self.existsTable()):
                with self.toDriver.connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM {} WHERE data_entrada_titulo = TO_CHAR('{}'::DATE, 'DD/MM/YYYY')".format(self.name, startDate))
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
            else:
                logger.info("Tabela não existe!")
                raise "Tabela não existe!"
        except Exception as e:
            logger.info("Erro ao tentar deletar registros da tabela {} entre as datas de {} e {}".format(self.name, startDate, endDate))
            raise e

    def createTable(self):
        creationQuery = """
        CREATE TABLE titulos_com_notas (
            cod_transacao VARCHAR(5) NULL,
            desc_transacao VARCHAR(60) NULL,
            data_entrada_titulo VARCHAR(10) NULL,
            empresa NUMERIC(4,0) NULL,
            filial_erp NUMERIC(5,0) NULL,
            nome_filial VARCHAR(30) NULL,
            seq_mov NUMERIC(4,0) NULL,
            filial_linx VARCHAR(3) NULL,
            cidade_filial VARCHAR(60) NULL,
            uf_filial VARCHAR(2) NULL,
            cod_cc_nfe VARCHAR(9) NULL,
            descr_cc_rat_nota VARCHAR(80) NULL,
            cod_contabil_nfe NUMERIC(38,0) NULL,
            descr_conta VARCHAR(250) NULL,
            valor_rat_nfe NUMERIC(15,2) NULL,
            data_emissao_titulo VARCHAR(10) NULL,
            nfe_titulo NUMERIC(9,0) NULL,
            serie_nf_entratata_titulo VARCHAR(3) NULL,
            venc_original VARCHAR(10) NULL,
            venc_prorrogada VARCHAR(10) NULL,
            data_pagto VARCHAR(10) NULL,
            cod_forma_pagto NUMERIC(2,0) NULL,
            descr_forma_pagto VARCHAR(30) NULL,
            situacao_titulo VARCHAR(2) NULL,
            titulo VARCHAR(15) NULL,
            cod_tipo VARCHAR(3) NULL,
            descr_tipo_titulo VARCHAR(40) NULL,
            cod_forn NUMERIC(9,0) NULL,
            nome_fornecedor VARCHAR(100) NULL,
            nome_fantasia_forn VARCHAR(50) NULL,
            cpnj_cpf NUMERIC(14,0) NULL,
            diferencial_icms NUMERIC(38,0) NULL,
            irrf NUMERIC(15,2) NULL,
            pis_recuperar NUMERIC(15,2) NULL,
            cofins_recuperar NUMERIC(15,2) NULL,
            csll NUMERIC(15,2) NULL,
            outras_retencoes NUMERIC(15,2) NULL,
            observacao VARCHAR(250) NULL,
            juros NUMERIC(15,2) NULL,
            multa NUMERIC(15,2) NULL,
            engargo NUMERIC(15,2) NULL,
            acrescimo NUMERIC(15,2) NULL,
            desconto NUMERIC(15,2) NULL,
            outros_descontos NUMERIC(15,2) NULL,
            num_ordem_compra NUMERIC(38,0) NULL,
            num_contrato NUMERIC(38,0) NULL,
            data_emissao_oc VARCHAR(10) NULL,
            nota_fiscal NUMERIC(9,0) NULL,
            nfe_seq_produto NUMERIC(3,0) NULL,
            produto VARCHAR(14) NULL,
            fam_produto VARCHAR(6) NULL,
            descr_fam_prod VARCHAR(50) NULL,
            descr_produto VARCHAR(250) NULL,
            cod_usu_ger_oc NUMERIC(38,0) NULL,
            nome_ger_oc VARCHAR(255) NULL,
            cod_usu_apr_oc NUMERIC(38,0) NULL,
            nome_usu_apr_oc VARCHAR(255) NULL,
            nivel_aprov_ordem_compra NUMERIC(38,0) NULL,
            cod_usu_ger_contr NUMERIC(38,0) NULL,
            nome_usu_ger_contr VARCHAR(255) NULL,
            cod_usu_apr_contr NUMERIC(38,0) NULL,
            nome_usu_apr_contr VARCHAR(255) NULL,
            nivel_aprov_contrato NUMERIC(38,0) NULL,
            cod_proced_oc NUMERIC(38,0) NULL,
            procedencia_oc VARCHAR(25) NULL,
            tipo CHAR(7) NULL,
            cod_sit_oc NUMERIC(38,0) NULL,
            situacao_oc VARCHAR(25) NULL
        );
        """
