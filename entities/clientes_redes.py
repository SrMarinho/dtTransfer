from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ClientesRedes(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'clientes_redes'
        self.columns = [
            "cliente_rede",
            "formulario_origem",
            "tab_master_origem",
            "reg_master_origem",
            "reg_log_inclusao",
            "descricao",
            "credito_unificado",
            "analisa_credito",
            "rede_grupo",
            "projeto"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_clientes_redes.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS clientes_redes
            (
                cliente_rede numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                descricao character varying(60) COLLATE pg_catalog."default",
                credito_unificado character varying(1) COLLATE pg_catalog."default",
                analisa_credito character varying(1) COLLATE pg_catalog."default",
                rede_grupo character varying(1) COLLATE pg_catalog."default",
                projeto numeric(15,0)
            );
        """
