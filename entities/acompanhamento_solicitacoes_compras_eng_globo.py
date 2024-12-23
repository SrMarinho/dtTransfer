from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class AcompanhamentoSolicitacoesComprasEngGlobo(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'acompanhamento_solicitacoes_compras_eng_globo'
        self.columns = [
            'produto_ou_servico',
            'tipo_compra',
            'situacao_solicitacao',
            'empresa',
            'filial_erp',
            'filial_linx',
            'cod_usu_solic',
            'usuario_solicitacao',
            'num_solicitacao',
            'fam_produto_servico',
            'descr_familia_produto_servico',
            'produto_servico',
            'seq',
            'descricao_servico_produto',
            'derivacao',
            'descr_derivacao',
            'cod_contabil',
            'descr_contabil',
            'cod_custo',
            'descr_custo',
            'qtda_solicitada',
            'observacao_solicitacao',
            'data_solicitacao',
            'data_emissao_ocp',
            'data_prev_entrega_solicitacao',
            'prev_entrega_servico_produto',
            'num_cotacao',
            'valor_ordem_compra',
            'qtda_ordem_compra',
            'valor_item_ordem_compra',
            'num_ordem_de_comp',
            'cod_fornecedor_nota',
            'nome_fantasia_fornecedor',
            'num_nota_fiscal',
            'data_entrada_nfe',
            'data_vencimento_titulo',
            'situacao_titulo',
            'procedencia_ordem_compra'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_acompanhamento_solicitacoes_compras_eng_globo.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS acompanhamento_solicitacoes_compras_eng_globo
            (
                produto_ou_servico character varying(1),
                tipo_compra character varying(13),
                situacao_solicitacao character varying(15),
                empresa numeric(4,0),
                filial_erp numeric(5,0),
                filial_linx character varying(3),
                cod_usu_solic numeric(10,0),
                usuario_solicitacao character varying(255),
                num_solicitacao numeric(9,0),
                fam_produto_servico character varying(6),
                descr_familia_produto_servico character varying(50),
                produto_servico character varying(14),
                seq numeric(6,0),
                descricao_servico_produto character varying(250),
                derivacao character varying(7),
                descr_derivacao character varying(50),
                cod_contabil numeric(7,0),
                descr_contabil character varying(250),
                cod_custo character varying(9),
                descr_custo character varying(80),
                qtda_solicitada numeric(14,5),
                observacao_solicitacao character varying(250),
                data_solicitacao character varying(10),
                data_emissao_ocp character varying(10),
                data_prev_entrega_solicitacao character varying(10),
                prev_entrega_servico_produto character varying(10),
                num_cotacao numeric(38,0),
                valor_ordem_compra numeric(38,2),
                qtda_ordem_compra numeric(38,0),
                valor_item_ordem_compra numeric(38,2),
                num_ordem_de_comp numeric(38,0),
                cod_fornecedor_nota numeric(38,0),
                nome_fantasia_fornecedor character varying(50),
                num_nota_fiscal numeric(38,0),
                data_entrada_nfe character varying(10),
                data_vencimento_titulo character varying(10),
                situacao_titulo character varying(10),
                procedencia_ordem_compra character varying(36),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP
            );
        """
