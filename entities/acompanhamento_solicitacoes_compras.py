from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class AcompanhamentoSolicitacoesCompras(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'acompanhamento_solicitacoes_compras'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_acompanhamento_solicitacoes_compras.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        print(f"Apagando registros no dia {startDate} na tabela {self.tableName}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_solicitacao = '{}';".format(self.tableName, startDate))
                print(f"Registros apagados com sucesso no dia {startDate} na tabela {self.tableName}!")
        except Exception as e:
            print(f"Erro ao tentar apagar registros no dia {startDate} na tabela {self.tableName}!")
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
