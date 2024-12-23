from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class GruposTributarios(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'grupos_tributarios'
        self.columns = [
            "grupo_tributario",
            "descricao",
            "data_hora",
            "usuario_logado",
            "cadastro_ativo",
            "observacao",
            "grupo_fiscal"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_grupos_tributarios.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS grupos_tributarios
            (
                grupo_tributario numeric(15,0),
                descricao character varying(120),
                data_hora timestamp without time zone,
                usuario_logado numeric(15,0),
                cadastro_ativo character varying(1),
                observacao text,
                grupo_fiscal numeric(15,0),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
