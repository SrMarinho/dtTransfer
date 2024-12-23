from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class Produto(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'produto'
        self.columns = [
            "codigo_produto",
            "ean",
            "dum",
            "descricao",
            "familia",
            "molecula",
            "franquia",
            "categoria",
            "classificacao",
            "situacao",
            "curva",
            "legenda",
            "embalagem",
            "laboratorio_id",
            "grupo_produto",
            "subgrupo_produto",
            "situacao_compra",
            "produto_resumo",
            "produto_resumo_descricao",
            "preco_monitorado",
            "cst_origem",
            "grupo_tributario",
            "grupo_tributario_entrada",
            "grupo_tributario_importados"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_produto.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS produto
            (
                codigo_produto integer,
                ean character varying(191),
                dum character varying(191),
                descricao character varying(191),
                familia character varying(191),
                molecula text,
                franquia character varying(191),
                categoria character varying(191),
                classificacao character varying(191),
                situacao character varying(1),
                curva character varying(2),
                legenda character varying(191),
                embalagem integer,
                laboratorio_id integer,
                grupo_produto character varying(191),
                subgrupo_produto character varying(191),
                situacao_compra integer,
                produto_resumo integer,
                produto_resumo_descricao character varying(191),
                preco_monitorado boolean DEFAULT true,
                cst_origem numeric(1,0),
                grupo_tributario numeric(15,0),
                grupo_tributario_entrada numeric(15,0),
                grupo_tributario_importados numeric(15,0),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT produto_pkey PRIMARY KEY (codigo_produto)
            );
        """
