from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FfolhaVisaoContabil(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'f_folha_visao_contabil'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_folha_visao_contabil.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        print(f"Apagando registros no dia {startDate} na tabela {self.tableName}...")
        try:
            with self.toDriver.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM {} A WHERE A.data_lancamento = TO_CHAR('{}'::DATE, 'DD/MM/YYYY');".format(self.tableName, startDate))
                print(f"Registros apagados com sucesso no dia {startDate} na tabela {self.tableName}!")
        except Exception as e:
            print(f"Erro ao tentar apagar registros no dia {startDate} na tabela {self.tableName}!")
            raise e

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS f_folha_visao_contabil
            (
                empresa integer,
                filial integer,
                nome_filial character varying(40),
                data_lancamento character varying(10),
                cod_opcao_contabilidade integer,
                opcao_contabilidade character varying(24),
                cod_historico integer,
                valor numeric(14,2),
                cod_custo character varying(18),
                descr_custo character varying(80),
                codred_debito integer,
                codred_credito integer,
                descr_cod_lig_conta_contabil character varying(100),
                debcre character varying(1),
                lote_contabil integer
            );
        """
