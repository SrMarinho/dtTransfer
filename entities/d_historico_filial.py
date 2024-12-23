from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 


class DhistoricoFilial(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.name = 'd_historico_filial'
        self.columns = [
            "numemp",
            "tipcol",
            "numcad",
            "datalt",
            "empatu",
            "codtap",
            "estpos",
            "postra",
            "codfil",
            "taborg",
            "numloc",
            "cadatu",
            "codccu",
            "natdes",
            "tipadm",
            "ficreg",
            "contov",
            "staacc",
            "motpos",
            "estcar",
            "codcar",
            "codmot",
            "codesc",
            "codtma",
            "turint",
            "horbas",
            "horsab",
            "horsem",
            "hordsr",
            "codmts",
            "codest",
            "valsal",
            "cplsal",
            "tipsal",
            "tipest",
            "clasal",
            "nivsal",
            "perdes",
            "perrea",
            "codsin",
            "numcra",
            "stahis",
            "confin",
            "codvin",
            "carvag",
            "socsin",
            "admeso",
            "trabhr",
            "codbhr"
        ]
    
    def getQuery(self) -> str:
        with open('sqls/consulta_d_historico_filial.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE d_historico_filial (
                numemp INTEGER,
                tipcol INTEGER,
                numcad INTEGER,
                datalt DATE NOT NULL,
                empatu INTEGER,
                codtap INTEGER,
                estpos INTEGER,
                postra VARCHAR(24),
                codfil INTEGER,
                taborg INTEGER,
                numloc INTEGER,
                cadatu INTEGER,
                codccu VARCHAR(18),
                natdes INTEGER,
                tipadm INTEGER,
                ficreg INTEGER,
                contov VARCHAR(1),
                staacc INTEGER,
                motpos INTEGER,
                estcar INTEGER,
                codcar VARCHAR(24),
                codmot INTEGER,
                codesc INTEGER,
                codtma INTEGER,
                turint INTEGER,
                horbas INTEGER,
                horsab INTEGER,
                horsem INTEGER,
                hordsr INTEGER,
                codmts INTEGER,
                codest INTEGER,
                valsal NUMERIC(13,4),
                cplsal NUMERIC(13,4),
                tipsal INTEGER,
                tipest INTEGER,
                clasal VARCHAR(5),
                nivsal VARCHAR(5),
                perdes NUMERIC(5,2),
                perrea NUMERIC(8,5),
                codsin INTEGER,
                numcra NUMERIC(12,0),
                stahis INTEGER,
                confin INTEGER,
                codvin INTEGER,
                carvag VARCHAR(24),
                socsin VARCHAR(1),
                admeso INTEGER,
                trabhr INTEGER,
                codbhr INTEGER
            );
        """
