from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Laboratorios(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'laboratorios'
        self.columns = [
            'codigo_fornecedor',
            'fornecedor',
            # 'grupo_economico',
            'codigo_comprador',
            'comprador',
            'entidade',
            'entidade_nome',
            'cnpj'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_laboratorios.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS laboratorios
            (
                codigo_fornecedor integer,
                fornecedor character varying(191),
                grupo_economico character varying(191),
                codigo_comprador integer,
                comprador character varying(191),
                entidade bigint,
                entidade_nome character varying(191),
                cnpj character varying(14),
                created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """
