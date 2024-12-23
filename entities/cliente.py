from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class Cliente(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'cliente'
        self.columns = [
            'codigo_cliente', 
            'cnpj', 
            'razao_social', 
            'nome_fantasia', 
            'codigo_rede', 
            'rede', 
            'codigo_grupo_cliente', 
            'grupo_cliente', 
            'endereco', 
            'bairro', 
            'cep', 
            'cidade', 
            'estado', 
            'telefone', 
            'email'
        ]
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_cliente.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS cliente
            (
                codigo_cliente integer,
                cnpj character varying(191),
                razao_social character varying(191),
                nome_fantasia character varying(191),
                codigo_rede integer,
                rede character varying(191),
                codigo_grupo_cliente integer,
                grupo_cliente character varying(191),
                endereco character varying(191),
                bairro character varying(191),
                cep character varying(191),
                cidade character varying(191),
                estado character varying(191),
                telefone character varying(191),
                email character varying(191),
                created_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp(0) without time zone DEFAULT CURRENT_TIMESTAMP
            )
        """
