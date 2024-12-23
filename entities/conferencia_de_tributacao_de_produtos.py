from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ConferenciaDeTributacaoDeProdutos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'conferencia_de_tributacao_de_produtos'
        self.columns = [
            "produto",
            "descricao",
            "estado_origem",
            "estado_destino",
            "ncm",
            "codigo_cest",
            "grupo_tributario",
            "grupo_tributario_entrada",
            "marca",
            "cst_origem",
            "entrada_cst",
            "entrada_icms_proprio",
            "entrada_icms_proprio_importacao",
            "entrada_icms_prec",
            "entrada_icms_st",
            "entrada_iva",
            "entrada_red_icms_st_prec",
            "entrada_iva_prec",
            "entrada_iva_prec_imp",
            "entrada_icms_regime_precificacao",
            "entrada_icms_prec_distr",
            "entrada_aliquota_ipi",
            "entrada_icms_reducao_base",
            "entrada_icms_reducao_base_importacao",
            "saida_transf_cst",
            "saida_transf_iva",
            "saida_transf_icms_normal",
            "saida_transf_icms_reducao_base",
            "saida_transf_icms_regime_precificacao",
            "saida_transf_icms_st",
            "saida_transf_icms_recup",
            "saida_transf_icms_apur",
            "entrada_transf_cst",
            "entrada_transf_icms_proprio",
            "entrada_transf_icms_proprio_importacao",
            "entrada_transf_icms_prec",
            "entrada_transf_icms_st",
            "entrada_transf_iva",
            "entrada_transf_red_icms_st_prec",
            "entrada_transf_iva_prec",
            "entrada_transf_iva_prec_imp",
            "entrada_transf_icms_prec_distr",
            "entrada_transf_aliquota_ipi",
            "entrada_transf_icms_reducao_base",
            "entrada_transf_icms_reducao_base_importacao",
            "saida_venda_cst",
            "saida_venda_iva",
            "saida_venda_icms_normal",
            "saida_venda_icms_reducao_base",
            "saida_venda_icms_regime_precificacao",
            "saida_venda_icms_st",
            "saida_venda_icms_recup",
            "tipo"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_conferencia_de_tributacao_de_produtos.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS conferencia_de_tributacao_de_produtos (
                            produto NUMERIC(15,0),
                            descricao VARCHAR(255),
                            estado_origem VARCHAR(2),
                            estado_destino VARCHAR(2),
                            ncm VARCHAR(255),
                            codigo_cest VARCHAR(255),
                            grupo_tributario NUMERIC(15,0),
                            grupo_tributario_entrada NUMERIC(15,0),
                            marca VARCHAR(255),
                            cst_origem NUMERIC(15,0),
                            entrada_cst VARCHAR(255),
                            entrada_icms_proprio NUMERIC,
                            entrada_icms_proprio_importacao NUMERIC,
                            entrada_icms_prec NUMERIC,
                            entrada_icms_st NUMERIC,
                            entrada_iva NUMERIC,
                            entrada_red_icms_st_prec NUMERIC,
                            entrada_iva_prec NUMERIC,
                            entrada_iva_prec_imp NUMERIC,
                            entrada_icms_regime_precificacao NUMERIC,
                            entrada_icms_prec_distr NUMERIC,
                            entrada_aliquota_ipi NUMERIC,
                            entrada_icms_reducao_base NUMERIC,
                            entrada_icms_reducao_base_importacao NUMERIC,
                            saida_transf_cst NUMERIC,
                            saida_transf_iva NUMERIC,
                            saida_transf_icms_normal NUMERIC,
                            saida_transf_icms_reducao_base NUMERIC,
                            saida_transf_icms_regime_precificacao NUMERIC,
                            saida_transf_icms_st NUMERIC,
                            saida_transf_icms_recup NUMERIC,
                            saida_transf_icms_apur NUMERIC,
                            entrada_transf_cst NUMERIC,
                            entrada_transf_icms_proprio NUMERIC,
                            entrada_transf_icms_proprio_importacao NUMERIC,
                            entrada_transf_icms_prec NUMERIC,
                            entrada_transf_icms_st NUMERIC,
                            entrada_transf_iva NUMERIC,
                            entrada_transf_red_icms_st_prec NUMERIC,
                            entrada_transf_iva_prec NUMERIC,
                            entrada_transf_iva_prec_imp NUMERIC,
                            entrada_transf_icms_prec_distr NUMERIC,
                            entrada_transf_aliquota_ipi NUMERIC,
                            entrada_transf_icms_reducao_base NUMERIC,
                            entrada_transf_icms_reducao_base_importacao NUMERIC,
                            saida_venda_cst NUMERIC,
                            saida_venda_iva NUMERIC,
                            saida_venda_icms_normal NUMERIC,
                            saida_venda_icms_reducao_base NUMERIC,
                            saida_venda_icms_regime_precificacao NUMERIC,
                            saida_venda_icms_st NUMERIC,
                            saida_venda_icms_recup NUMERIC,
                            tipo INTEGER DEFAULT 1
                        );
        """
