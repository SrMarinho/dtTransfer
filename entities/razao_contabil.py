from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RazaoContabil(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'razao_contabil'
        self.columns = [
            'codtns', 
            'destns', 
            'empresa', 
            'filial_erp', 
            'nome_filial', 
            'seq_mov', 
            'filial_linx', 
            'cidade', 
            'uf', 
            'cod_cc_rateio_titulo', 
            'descr_cc_rateio', 
            'cod_contabil_rat_titulo', 
            'desc_conta_contabil_rateio_titulo', 
            'data_emissao_titulo', 
            'nf_entrada_titulo', 
            'serie_nf_entrada_titulo', 
            'vcto_original', 
            'vencimento', 
            'ult_pagto', 
            'data_pagamento', 
            'cod_forma_pgto', 
            'des_forma_pgto', 
            'situacao_titulo', 
            'titulo', 
            'tipo_tpt', 
            'des_tipo', 
            'des_tipo_fpg', 
            'cod_forn', 
            'nome_forn', 
            'nome_fantasia_forn', 
            'cpnj_cpf', 
            'filial_nfs', 
            'serie_nfs', 
            'nf_saida', 
            'valor_rateio', 
            'vlrcta', 
            'irrf', 
            'iss', 
            'inss', 
            'pis', 
            'cofins',
            'csll', 
            'outras_retencoes', 
            'total',
            'valor_aberto', 
            'observacao', 
            'valor_juros', 
            'valor_multa', 
            'valor_encargo', 
            'valor_acrescimo', 
            'valor_desconto', 
            'valor_outros_descontos', 
            'num_ordem_compra', 
            'num_nota_fiscal', 
            'data_emissao', 
            'seq_produto', 
            'codigo_produto', 
            'descricao_produto', 
            'observacao_ordem_compra', 
            'cod_usuario_geracao_ordem_compra', 
            'nome_usuario_geracao', 
            'cod_usuario_aprovador_oc', 
            'nome_usuario_aprovador_oc', 
            'nivel_usuario_oc', 
            'tipo', 
            'situacao_ordem_compra', 
            'data_entrada'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_pedidos_vendas.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
        """
