from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Espelho(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'espelho'
        self.columns = [
            "nf_compra_produto",
            "nf_compra",
            "produto",
            "operacao_fiscal",
            "fator_embalagem",
            "quantidade",
            "quantidade_estoque",
            "markup",
            "iva",
            "icms_substituto",
            "aliquota_icms",
            "icms_venda",
            "ipi_compra",
            "icms_compra",
            "desconto_compra",
            "fabrica",
            "venda_sugerida",
            "total_custo",
            "preco_maximo",
            "desconto_padrao",
            "preco_venda",
            "rentabilidade",
            "desconto_financeiro",
            "desconto_total",
            "diferenca",
            "nf_numero",
            "nf_serie",
            "nf_especie",
            "entidade",
            "empresa",
            "filial",
            "movimento",
            "total_produtos",
            "total_ipi",
            "total_despesas",
            "total_frete",
            "total_seguro",
            "total_substituicao",
            "total_repasse",
            "total_servicos",
            "total_geral",
            "icms_base_calculo",
            "icms_valor",
            "valor_unitario",
            "total_vendor",
            "fator_vendor",
            "iva_ajustado",
            "icms_subst_valor",
            "icms_subst_valor_pagar",
            "valor_produto_liquido",
            "valor_ipi",
            "icms_credito",
            "icms_decreto_35346",
            "despesas",
            "frete",
            "seguro",
            "repasse",
            "valor_pis",
            "valor_cofins",
            "custo",
            "custo_sem_bonif",
            "custo_anterior",
            "quantidade_embalagem",
            "iva_inter_estadual",
            "custo_final_liquido",
            "custo_unitario_conhecimento_frete",
            "custo_sem_frete",
            "nf_compra_anterior",
            "icms_desonerado_unit",
            "icms_st_retido_valor",
            "icms_valor_fpobreza_st",
            "custo_validacao",
            "estado"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_espelho.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS espelho
            (
                nf_compra_produto numeric(15,0),
                nf_compra numeric(15,0),
                produto numeric(15,0),
                operacao_fiscal numeric(5,0),
                fator_embalagem numeric(7,2),
                quantidade numeric(15,2),
                quantidade_estoque numeric(15,2),
                markup numeric(6,2),
                iva numeric(15,2),
                icms_substituto numeric(15,2),
                aliquota_icms numeric(10,2),
                icms_venda numeric(20,2),
                ipi_compra numeric(20,2),
                icms_compra numeric(20,2),
                desconto_compra numeric(20,2),
                fabrica numeric(20,2),
                venda_sugerida numeric(20,2),
                total_custo numeric(20,2),
                preco_maximo numeric(20,2),
                desconto_padrao numeric(20,2),
                preco_venda numeric(20,2),
                rentabilidade numeric(20,2),
                desconto_financeiro numeric(20,2),
                desconto_total numeric(20,2),
                diferenca numeric(20,2),
                nf_numero numeric(9,0),
                nf_serie character varying(3) COLLATE pg_catalog."default",
                nf_especie character varying(3) COLLATE pg_catalog."default",
                entidade numeric(15,0),
                empresa numeric(15,0),
                filial numeric(5,0),
                movimento timestamp without time zone,
                total_produtos numeric(20,2),
                total_ipi numeric(20,2),
                total_despesas numeric(20,2),
                total_frete numeric(20,2),
                total_seguro numeric(20,2),
                total_substituicao numeric(20,2),
                total_repasse numeric(20,2),
                total_servicos numeric(20,2),
                total_geral numeric(20,2),
                icms_base_calculo numeric(20,2),
                icms_valor numeric(20,2),
                valor_unitario numeric(20,2),
                total_vendor numeric(15,2),
                fator_vendor numeric(15,6),
                iva_ajustado numeric(15,2),
                icms_subst_valor numeric(15,4),
                icms_subst_valor_pagar numeric(15,4),
                valor_produto_liquido numeric(15,4),
                valor_ipi numeric(15,4),
                icms_credito numeric(15,4),
                icms_decreto_35346 numeric(15,4),
                despesas numeric(15,4),
                frete numeric(15,4),
                seguro numeric(15,4),
                repasse numeric(15,4),
                valor_pis numeric(15,4),
                valor_cofins numeric(15,4),
                custo numeric(15,4),
                custo_sem_bonif numeric(15,4),
                custo_anterior numeric(15,2),
                quantidade_embalagem numeric(4,0),
                iva_inter_estadual numeric(15,2),
                custo_final_liquido numeric(15,2),
                custo_unitario_conhecimento_frete numeric(15,4),
                custo_sem_frete numeric(15,4),
                nf_compra_anterior numeric(15,0),
                icms_desonerado_unit numeric(15,4),
                icms_st_retido_valor numeric(15,4),
                icms_valor_fpobreza_st numeric(15,2),
                custo_validacao numeric(15,4),
                estado character varying(2) COLLATE pg_catalog."default",
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
