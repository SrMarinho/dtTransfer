from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class MarcacoesPonto(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'marcacoes_ponto'
        self.columns = [
            "empresa",
            "data_acesso",
            "hora_acesso",
            "data_apuracao",
            "codigo_site",
            "descr_site",
            "coletor",
            "descr_coletor",
            "cod_funcao",
            "origem_marcacao",
            "uso_marcacao",
            "tipo_acesso",
            "matricula",
            "direcao_acesso",
            "excluido_do_ponto",
            "min_to_hour"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_marcacoes_ponto.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS marcacoes_ponto
            (
                data_acesso character varying(10),
                hora_acesso numeric(5,0),
                data_apuracao character varying(10),
                codigo_site numeric(5,0),
                descr_site character varying(30),
                coletor numeric(5,0),
                descr_coletor character varying(50),
                cod_funcao numeric(2,0),
                origem_marcacao character varying(1),
                uso_marcacao numeric(2,0),
                tipo_acesso numeric(3,0),
                matricula numeric(12,0),
                direcao_acesso character varying(1),
                excluido_do_ponto character varying(1),
                min_to_hour character varying(13),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
