from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class VansProjetos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'vans_projetos'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_vans_projetos.sql', 'r') as file:
            return file.read()

    def deleteDateBetween(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS vans_projetos
            (
                projeto numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                descricao_projeto character varying(60),
                usuario_logado numeric(15,0),
                data_hora timestamp without time zone,
                identificador numeric(15,0),
                projeto_depara character varying(20),
                ativo character varying(1),
                sigla_projeto_layout_edi character varying(20)
            );
        """
