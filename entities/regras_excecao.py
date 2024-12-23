from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RegrasExcecao(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'regras_excecao'
        self.columns = [
            'nivel', 
            'configuracao_ol', 
            'cod_usuario', 
            'usuario', 
            'data_hora', 
            'descricao', 
            'projeto', 
            'descricao_projeto', 
            'identificador', 
            'descricao_identificador', 
            'validade_inicial', 
            'validade_final', 
            'marca', 
            'marca_descricao', 
            'desconto_total', 
            'desconto_distribuidora', 
            'desconto_fabricante', 
            'tipo_acao_desconto_marcas', 
            'empresa', 
            'descricao_empresa', 
            'rd_desconto_de_ini', 
            'rd_desconto_de_fim', 
            'rd_desconto_para', 
            'rd_desconto_para_distribuidora', 
            'rd_desconto_para_industria', 
            'tipo_acao_desconto_regras', 
            'produto', 
            'descricao_produto', 
            'desconto_distribuidora_produto', 
            'desconto_industria', 
            'desconto_final', 
            'tipo_acao_desconto_produtos', 
            'ol_apontadores', 
            'descricao_ol_apontadores', 
            'cod_cliente', 
            'cliente', 
            'cod_grupo', 
            'descricao_grupo', 
            'cod_rede', 
            'descricao_rede'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
