from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ConfiguracoesOlExcecoesDescontos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'configuracoes_ol_excecoes_descontos'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_configuracoes_ol_excecoes_descontos.sql', 'r') as file:
            return file.read()

    def deleteDateBetween(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS configuracoes_ol_excecoes_descontos
            (
                configuracao_ol_excecao_des numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                configuracao_ol_excecao numeric(15,0),
                desconto_de_ini numeric(6,2),
                desconto_de_fim numeric(6,2),
                desconto_para numeric(6,2),
                tipo_acao_desconto numeric(5,0),
                desconto_para_distribuidora numeric(6,2),
                desconto_para_industria numeric(6,2),
                contador_f3 numeric(15,0)
            );
        """
