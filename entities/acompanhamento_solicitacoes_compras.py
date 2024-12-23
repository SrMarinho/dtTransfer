from config.logger.logging import logger
from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class AcompanhamentoSolicitacoesCompras(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'acompanhamento_solicitacoes_compras'
        self.columns = [
            "produto_ou_servico",
            "empresa",
            "filial",
            "deposito",
            "num_solicitacao",
            "produto_servico",
            "seq",
            "descricao_servico_produto",
            "derivacao",
            "qnt_solicitada",
            "qnt_cotada",
            "observacao_solicitacao",
            "data_solicitacao",
            "data_cotacao",
            "data_emissao_ocp",
            "data_prev_entrega_solicitacao",
            "prev_entrega_produto_servico",
            "num_cotacao",
            "fornecedor",
            "prazo_entrega",
            "cod_cond_pag",
            "descr_cond_pag",
            "derivacao_cot",
            "preco_cotado",
            "valor_cotacao",
            "vlrprs",
            "valor_desconto",
            "valor_fcp",
            "perc_desc_cot",
            "usuario_cotacao",
            "nome_usuario",
            "ciffob",
            "num_ordem_de_comp",
            "filial_ocp",
            "observacao_ocp"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_acompanhamento_solicitacoes_compras.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        logger.info(f"{self.name} - Apagando registros no dia {startDate}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_solicitacao = '{}';".format(self.name, startDate))
                logger.info(f"{self.name} - Registros apagados com sucesso no dia {startDate}!")
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar apagar registros no dia {startDate}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE acompanhamento_solicitacoes_compras (
                produto_ou_servico varchar(1),
                empresa integer,
                filial integer,
                deposito varchar(10),
                num_solicitacao integer,
                produto_servico varchar(14),
                seq integer,
                descricao_servico_produto varchar(250),
                derivacao varchar(7),
                qnt_solicitada numeric(14,5),
                qnt_cotada numeric(14,5),
                observacao_solicitacao varchar(250),
                data_solicitacao date,
                data_cotacao date,
                data_emissao_ocp date,
                data_prev_entrega_solicitacao date,
                prev_entrega_produto_servico date,
                num_cotacao integer,
                fornecedor integer,
                prazo_entrega integer,
                cod_cond_pag varchar(6),
                descr_cond_pag varchar(50),
                derivacao_cot varchar(7),
                preco_cotado numeric(21,10),
                valor_cotacao numeric(15,2),
                vlrprs numeric(15,2),
                valor_desconto numeric(15,2),
                valor_fcp numeric(15,2),
                perc_desc_cot numeric(7,4),
                usuario_cotacao integer,
                nome_usuario varchar(255),
                ciffob varchar(1),
                num_ordem_de_comp integer,
                filial_ocp integer,
                observacao_ocp varchar(1000)
            );
        """
