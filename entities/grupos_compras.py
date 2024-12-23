from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class GruposCompras(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'grupos_compras'
        self.columns = [
            "grupo_compra",
            "descricao",
            "empresa",
            "data_hora",
            "usuario_logado",
            "obrigatorio_aprovacao",
            "dias_curva_a",
            "dias_curva_b",
            "dias_curva_c",
            "leadtime",
            "comprador",
            "dias_curva_d",
            "dias_curva_e",
            "fornecedor",
            "leadtime_teorico",
            "dias_emissao",
            "data_hora_atualizacao_lt",
            "vincular_comprador",
            "leadtime_acordado",
            "marca"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_grupos_compras.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS grupos_compras
            (
                grupo_compra numeric(15,0),
                descricao character varying(60),
                data_hora timestamp without time zone,
                usuario_logado numeric(15,0),
                obrigatorio_aprovacao character varying(1),
                dias_curva_a numeric(4,0),
                dias_curva_b numeric(4,0),
                dias_curva_c numeric(4,0),
                leadtime numeric(5,0),
                comprador numeric(15,0),
                dias_curva_d numeric(4,0),
                dias_curva_e numeric(4,0),
                fornecedor numeric(15,0),
                leadtime_teorico numeric(5,0),
                dias_emissao numeric(15,0),
                data_hora_atualizacao_lt timestamp without time zone,
                vincular_comprador character varying(1),
                created_at time without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
