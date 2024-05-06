from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ConfiguracoesOlExcecoesUnidades(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'configuracoes_ol_excecoes_unidades'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_configuracoes_ol_excecoes_unidades.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS configuracoes_ol_unidades
            (
                configuracao_ol_unidade numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                configuracao_ol numeric(15,0),
                empresa numeric(15,0),
                tipo_restricao numeric(1,0),
                contador_f4 numeric(15,0)
            );
        """
