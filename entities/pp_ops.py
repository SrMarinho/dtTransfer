from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class PpOps(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'pp_ops'
        self.columns = [
           'formulario_origem', 
           'tab_master_origem', 
           'reg_master_origem', 
           'registro_procift', 
           'nf_numero', 
           'empresa', 
           'emissao', 
           'operacao_fiscal', 
           'data_hora', 
           'chave_nfe', 
           'usuario', 
           'usuario_nome', 
           'status', 
           'produto', 
           'descricao_produto', 
           'quantidade', 
           'total_produto', 
           'total_produtos', 
           'total_geral', 
           'formulario', 
           'validade'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
