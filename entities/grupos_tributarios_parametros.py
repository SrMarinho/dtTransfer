from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class GruposTributariosParametros(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'grupos_tributarios_parametros'
        self.columns = [
            "grupo_tributario_parametro",
            "grupo_tributario",
            "grupo_local",
            "tipo_icms",
            "situacao_tributaria",
            "aliquota_icms",
            "icms_substituto",
            "iva",
            "iva_ajustado",
            "observacao_fiscal",
            "aliquota_icms_decreto_35346",
            "operacao_fiscal",
            "estado_origem",
            "estado_destino",
            "fator_reducao_st",
            "icms_reducao_base",
            "situacao_tributaria_ipi",
            "tipo_ipi",
            "aliquota_ipi",
            "ipi_reducao_base",
            "situacao_tributaria_pis",
            "aliquota_pis",
            "situacao_tributaria_cofins",
            "aliquota_cofins",
            "pis_cofins_tributado",
            "carga_tributos_lei12741",
            "tipo_icms_transf",
            "calc_base_icms_normal",
            "calc_base_icms_st",
            "calc_reducao_base_icms",
            "calc_base_icms_st_retido",
            "icms_isento",
            "icms_outros",
            "tipo_grupo_tributario",
            "situacao_tributaria_transf",
            "realiza_operacao_crossdocking",
            "margem_crossdoking",
            "aliquota_icms_suframa",
            "icms_aliquota_fpobreza",
            "aliquota_despesas_st",
            "aliquota_ma_st_apuracao",
            "aliquota_repasse",
            "repasse_aliquota",
            "tipo_escrituracao",
            "situacao_tributaria_preco_tabelado",
            "icms_aliquota_fpobreza_st",
            "aliquota_icms_desonerado",
            "icms_regime_precificacao",
            "aplicar_alteracao_cfop",
            "cal_icms_st_valor_liq",
            "inativo",
            "icms_aliquota_desonerado",
            "tipo_icms_desonerado"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_grupos_tributarios_parametros.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS grupos_tributarios_parametros
            (
                grupo_tributario_parametro numeric(15,0),
                grupo_tributario numeric(15,0),
                grupo_local numeric(15,0),
                tipo_icms numeric(2,0),
                situacao_tributaria character varying(3),
                aliquota_icms numeric(4,2),
                icms_substituto numeric(11,2),
                iva numeric(6,2),
                iva_ajustado numeric(7,2),
                observacao_fiscal numeric(15,0),
                aliquota_icms_decreto_35346 numeric(6,2),
                operacao_fiscal numeric(5,0),
                estado_origem character varying(2),
                estado_destino character varying(2),
                fator_reducao_st numeric(6,3),
                icms_reducao_base numeric(6,3),
                situacao_tributaria_ipi character varying(2),
                tipo_ipi numeric(2,0),
                aliquota_ipi numeric(5,2),
                ipi_reducao_base numeric(6,2),
                situacao_tributaria_pis character varying(2),
                aliquota_pis numeric(6,2),
                situacao_tributaria_cofins character varying(2),
                aliquota_cofins numeric(6,2),
                pis_cofins_tributado character varying(1),
                carga_tributos_lei12741 numeric(6,2),
                tipo_icms_transf numeric(2,0),
                calc_base_icms_normal character varying(1),
                calc_base_icms_st character varying(1),
                calc_reducao_base_icms character varying(1),
                calc_base_icms_st_retido character varying(1),
                icms_isento character varying(1),
                icms_outros character varying(1),
                tipo_grupo_tributario numeric(15,0),
                situacao_tributaria_transf character varying(3),
                realiza_operacao_crossdocking character varying(1),
                margem_crossdoking numeric(6,2),
                aliquota_icms_suframa numeric(15,2),
                icms_aliquota_fpobreza numeric(6,2),
                aliquota_despesas_st numeric(15,6),
                aliquota_ma_st_apuracao numeric(15,6),
                aliquota_repasse numeric(15,6),
                repasse_aliquota numeric(15,6),
                tipo_escrituracao numeric(6,0),
                situacao_tributaria_preco_tabelado character varying(3),
                icms_aliquota_fpobreza_st numeric(6,4),
                aliquota_icms_desonerado numeric(15,2),
                icms_regime_precificacao numeric(6,2),
                aplicar_alteracao_cfop character varying(1),
                cal_icms_st_valor_liq character varying(1),
                inativo character varying(1),
                icms_aliquota_desonerado numeric(15,2),
                tipo_icms_desonerado numeric(15,0),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
