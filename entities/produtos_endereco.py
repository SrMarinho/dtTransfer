from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class ProdutosEndereco(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'produtos_endereco'
        self.columns = [
            'produto', 
            'descricao', 
            'ean', 
            'corredor', 
            'embalagem_industria', 
            'fator_embalagem', 
            'localizador', 
            'capacidade_cubagem', 
            'capacidade_cubagem_minimo', 
            'estoque_total', 
            'curva', 
            'centro_estoque'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_produtos_endereco.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS produtos_endereco
            (
                produto numeric(15,0),
                descricao character varying(255),
                ean character varying(60),
                corredor character varying(10),
                embalagem_industria numeric(6,0),
                fator_embalagem numeric(5,0),
                localizador character varying(60),
                capacidade_cubagem numeric(15,0),
                capacidade_cubagem_minimo numeric(15,0),
                estoque_total numeric(15,4),
                curva character varying(1) COLLATE pg_catalog."default",
                centro_estoque numeric(15,0),
                created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
