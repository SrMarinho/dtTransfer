from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class FMapearContasLancContabil(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'f_mapear_contas_lanc_contabil'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_f_mapear_contas_lanc_contabil.sql', 'r') as file:
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
            CREATE TABLE f_mapear_contas_lanc_contabil (
                empresa INTEGER,
                num_lancam INTEGER,
                origem VARCHAR(3),
                filial INTEGER,
                data_lancamento VARCHAR(10),
                debito INTEGER,
                valor NUMERIC(14,2),
                lote INTEGER,
                cod_historico INTEGER,
                descr_historico VARCHAR(80),
                cpllct VARCHAR(250),
                cod_custo VARCHAR(9),
                descr_custo VARCHAR(80),
                deb_cred VARCHAR(1)
            );
        """
