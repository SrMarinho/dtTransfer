from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 
from config.databases.biMktNaz import BiMktNaz

class ConfiguracoesOlExcecoesMarcas(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'PbsNazariaDados'
        self.toDB = 'biMktNaz'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'configuracoes_ol_excecoes_marcas'
        self.columns = [
            "configuracao_ol_excecao_marca",
            "formulario_origem",
            "tab_master_origem",
            "reg_master_origem",
            "reg_log_inclusao",
            "configuracao_ol_excecao",
            "marca",
            "desconto_total",
            "desconto_distribuidora",
            "desconto_fabricante",
            "tipo_acao_desconto",
            "contador_f1",
            "desconto_de_ini",
            "desconto_de_fim"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_configuracoes_ol_excecoes_marcas.sql', 'r') as file:
            return file.read()

    def deleteDay(self, startDate, endDate):
        ...

    def createTable(self):
        creationQuery = """
            CREATE TABLE IF NOT EXISTS configuracoes_ol_excecoes_marcas
            (
                configuracao_ol_excecao_marca numeric(15,0),
                formulario_origem numeric(6,0),
                tab_master_origem numeric(6,0),
                reg_master_origem numeric(15,0),
                reg_log_inclusao numeric(15,0),
                configuracao_ol_excecao numeric(15,0),
                marca numeric(15,0),
                desconto_total numeric(20,2),
                desconto_distribuidora numeric(15,2),
                desconto_fabricante numeric(15,2),
                tipo_acao_desconto numeric(5,0),
                contador_f1 numeric(15,0),
                desconto_de_ini numeric(6,2),
                desconto_de_fim numeric(6,2)
            );
        """
