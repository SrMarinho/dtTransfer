from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class CfopFiscal(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'cfop_fiscal'
        self.columns = [
            'tipo',
            'empresa',
            'filial_erp',
            'filial_linx',
            'cfop',
            'transacao',
            'valor_contabil',
            'base_icms',
            'valor_icms',
            'valor_isento_icms',
            'valor_outros_icms',
            'total',
            'data_evento'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_cfop_fiscal.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE cfop_fiscal (
                empresa numeric(4,0) NULL,
                filial_erp numeric(5,0) NULL,
                filial_linx varchar(3) NULL,
                cfop varchar(5) NULL,
                transacao varchar(5) NULL,
                dt_entrada date NULL,
                valor_contabil numeric(38,0) NULL,
                base_icms numeric(38,0) NULL,
                valor_icms numeric(38,0) NULL,
                valor_isento_icms numeric(38,0) NULL,
                valor_outros_icms numeric(38,0) NULL,
                total numeric(38,0) NULL
            );
        """
