from entities.queryable import Queryable
from factories.database_factory import DatabaseFactory 

class DEventos(Queryable):
    def __init__(self, params):
        self.params = params
        self.fromDB = 'Senior'
        self.toDB = 'biSenior'
        self.fromDriver = DatabaseFactory.getInstance(self.fromDB)
        self.toDriver = DatabaseFactory.getInstance(self.toDB)
        self.tableName = 'd_eventos'
    
    def getQuery(self) -> str:
        with open('sqls/consulta_d_eventos.sql', 'r') as file:
            return file.read()

    def createTable(self):
        creationQuery = """
            CREATE TABLE d_eventos (
                codtab INTEGER,
                codeve INTEGER,
                deseve VARCHAR(25),
                crteve VARCHAR(3),
                codcrt INTEGER,
                horuti VARCHAR(1),
                rgreve INTEGER,
                rgresp INTEGER,
                tipeve INTEGER,
                nateve INTEGER,
                sinsel VARCHAR(1),
                codsel INTEGER,
                valcal NUMERIC(13,4),
                valtet NUMERIC(11,2),
                codclc INTEGER,
                alfaev VARCHAR(10),
                tipinf VARCHAR(1),
                dimnor VARCHAR(1),
                gereve INTEGER,
                prjeve VARCHAR(1),
                pereve VARCHAR(1),
                codsin INTEGER,
                rateve VARCHAR(1),
                tiprat INTEGER,
                remcag VARCHAR(1),
                evedpo INTEGER,
                evedne INTEGER,
                arrval INTEGER,
                arrpre INTEGER,
                arresp INTEGER,
                rempat VARCHAR(1),
                rubhom INTEGER,
                obseve VARCHAR(255),
                inival DATE,
                fimval DATE,
                descom VARCHAR(100)
            );
        """
