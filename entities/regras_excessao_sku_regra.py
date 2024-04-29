from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class RegrasExcessaoSkuRegra(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'regras_excessao_sku_regra'
    
    def getQuery(self) -> str:
        try:
            with open('sqls/consulta_regras_excessao_sku_regra.sql', 'r') as file:
                return file.read()
        except Exception as e:
            raise e

    def deleteDay(self, startDate, endDate):
        try:
            if (self.existsTable()):
                conn = self.toDriver.connection()
                cursor = conn.cursor()
                cursor.execute(f"""
                               DELETE 
                               FROM
                                {self.tableName}
                               WHERE
                                data_hora BETWEEN '{startDate}' AND '{endDate}';
                               """)

                conn.commit()
                conn.close()
                print(f"Foram deletados {cursor.rowcount} registro no dia {startDate} ao dia {endDate}.")
            else:
                raise "Tabela não existe!"
            
        except Exception as e:
            print("Erro ao tentar deletar registros da tabela {} entre as datas de {} e {}.".format(self.tableName, startDate, endDate))
            raise e

    def createTable(self):
        creationQuery = """
                    CREATE TABLE regras_excessao_sku_regra (
                        nivel varchar(11),
                        configuracao_ol numeric(15, 0),
                        cod_usuario numeric(15, 0),
                        usuario varchar(60),
                        data_hora timestamp(3),
                        descricao varchar(60),
                        projeto numeric(15, 0),
                        descricao_projeto varchar(60),
                        identificador numeric(15, 0),
                        descricao_identificador varchar(60),
                        validade_inicial timestamp(3),
                        validade_final timestamp(3),
                        marca numeric(15, 0),
                        marca_descricao varchar(60),
                        desconto_total_ma numeric(22,2),
                        desconto_distribuidora_ma numeric(17,2),
                        desconto_fabricante_ma numeric(17,2),
                        desconto_de_ini_ma numeric(8,2),
                        desconto_de_fim_ma numeric(8,2),
                        tipo_acao_desconto_ma varchar(60),
                        empresa numeric(15, 0),
                        descricao_empresa varchar(30),
                        rd_desconto_de_ini numeric(8,2),
                        rd_desconto_de_fim numeric(8,2),
                        rd_desconto_para numeric(8,2),
                        rd_desconto_para_distribuidora numeric(8,2),
                        rd_desconto_para_industria numeric(8,2),
                        tipo_acao_desconto varchar(60),
                        produto numeric(15, 0),
                        descricao_produto varchar(255),
                        desconto_distribuidora_prod numeric(8,2),
                        desconto_industria_prod numeric(8,2),
                        desconto_final_prod numeric(8,2),
                        tipo_acao_desconto_prod varchar(60),
                        ol_apontadores numeric(15, 0),
                        descricao_ol_apontadores varchar(60),
                        cod_cliente numeric(15, 0),
                        cliente varchar(60),
                        cod_tipo_restricao numeric(15, 0),
                        tipo_restricao varchar(60),
                        cod_grupo numeric(15, 0),
                        descricao_grupo varchar(60),
                        cod_rede numeric(15, 0),
                        descricao_rede varchar(60)
                    );
        """
