from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class VendasBoletos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'vendas_boletos'
        self.columns = [
            'venda_boleto', 
            'registro_procfit', 
            'dias', 
            'vencimento', 
            'percentual', 
            'valor', 
            'titulo'
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_vendas_boletos.sql', 'r') as file:
            return file.read()
