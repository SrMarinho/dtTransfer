from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class GruposTributariosEntrada(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'grupos_tributarios_entrada'
        self.columns = [
            "grupo_tributario_entrada",
            "descricao",
            "data_hora",
            "usuario_logado",
            "tipo_ipi",
            "aliquota_ipi",
            "aliquota_pis",
            "aliquota_cofins",
            "classif_fiscal_codigo",
            "pis_cofins_tributado",
            "cadastro_ativo",
            "lista_pnu",
            "situacao_tributaria_cofins",
            "situacao_tributaria_pis",
            "situacao_tributaria",
            "ipi_reducao_base",
            "grupo_fiscal"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_grupos_tributarios_entrada.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS public.grupos_tributarios_entrada
            (
                grupo_tributario_entrada numeric(15,0),
                descricao character varying(60) COLLATE pg_catalog."default",
                data_hora timestamp without time zone,
                usuario_logado numeric(15,0),
                tipo_ipi numeric(2,0),
                aliquota_ipi numeric(5,2),
                aliquota_pis numeric(6,2),
                aliquota_cofins numeric(6,2),
                classif_fiscal_codigo character varying(13) COLLATE pg_catalog."default",
                pis_cofins_tributado character varying(1) COLLATE pg_catalog."default",
                cadastro_ativo character varying(1) COLLATE pg_catalog."default",
                lista_pnu character varying(1) COLLATE pg_catalog."default",
                situacao_tributaria_cofins character varying(2) COLLATE pg_catalog."default",
                situacao_tributaria_pis character varying(2) COLLATE pg_catalog."default",
                situacao_tributaria character varying(3) COLLATE pg_catalog."default",
                ipi_reducao_base numeric(6,2),
                grupo_fiscal numeric(15,0),
                created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
