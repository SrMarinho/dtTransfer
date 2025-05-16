from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ConfiguracoesOlMarcas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'configuracoes_ol_marcas'
        self.columns = [
            "configuracao_ol_marca",
            "configuracao_ol",
            "marca",
            "contador_f9",
            "desconto_total",
            "desconto_distribuidora",
            "desconto_fabricante",
            "cashback_pontuacao",
            "cashback_resgate",
            "desconto_fabricante_01",
            "desconto_fabricante_02",
            "desconto_fabricante_03",
            "desconto_fabricante_04",
            "desconto_fabricante_05"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_configuracoes_ol_marcas.sql', 'r') as file:
            return file.read()