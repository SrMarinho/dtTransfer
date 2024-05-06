from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ConfiguracoesOl(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'configuracoes_ol'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_configuracoes_ol.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.configuracoes_ol
            (
                configuracao_ol numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                descricao character varying(60),
                validade_inicial timestamp without time zone,
                validade_final timestamp without time zone,
                valor_fatura_minima numeric(15,2),
                quantidade_minima numeric(15,0),
                numero_itens numeric(15,0),
                segunda character varying(1),
                terca character varying(1),
                quarta character varying(1),
                quinta character varying(1),
                sexta character varying(1),
                sabado character varying(1),
                domingo character varying(1),
                usuario_logado numeric(15,0),
                data_hora timestamp without time zone,
                hora_inicial character varying(5),
                hora_final character varying(5),
                tipo_limitacao numeric(15,0),
                tipo_ol character varying(2),
                projeto numeric(15,0),
                identificador numeric(15,0),
                projeto_industria numeric(15,0),
                canal_autorizador character varying(1),
                condicao_comercial_canal_autorizador character varying(10),
                sigla_industria_ca character varying(10),
                processa_b2b character varying(1),
                tipo_cashback_pontuacao numeric(15,0),
                tipo_cashback_resgate numeric(15,0),
                observacao character varying(50)
            );
        """
