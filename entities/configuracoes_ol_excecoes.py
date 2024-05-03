from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ConfiguracoesOlExcecoes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'configuracoes_ol_excecoes'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_configuracoes_ol_excecoes.sql', 'r') as file:
            return file.read()

    def deleteDateBetween(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS configuracoes_ol_excecoes
            (
                configuracao_ol_excecao numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                usuario_logado numeric(15,0),
                data_hora timestamp without time zone,
                descricao character varying(60),
                validade_inicial timestamp without time zone,
                validade_final timestamp without time zone,
                entidade numeric(15,0),
                cliente_rede numeric(15,0),
                grupo_cliente numeric(15,0),
                tipo_origem_desconto numeric(5,0),
                identificador numeric(15,0),
                projeto numeric(15,0)
            );
        """
