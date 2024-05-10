from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FolhaControladoria(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'folha_controladoria'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_folha_controladoria.sql', 'r') as file:
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
            CREATE TABLE folha_controladoria (
                empresa INTEGER,
                filial INTEGER,
                nome_filial VARCHAR(40),
                data_lancamento VARCHAR(10),
                cod_opcao_contabilidade INTEGER,
                opcao_contabilidade VARCHAR(24),
                cod_historico INTEGER,
                valor NUMERIC(14,2),
                cod_custo VARCHAR(18),
                descr_custo VARCHAR(80),
                codred_debito INTEGER,
                codred_credito INTEGER,
                descr_cod_lig_conta_contabil VARCHAR(100),
                debcre VARCHAR(1),
                lote_contabil INTEGER
            );
        """
