from entities.queryable import Queryable

class Venda(Queryable):
    def __init__(self):
        ...
    
    @staticmethod
    def getQuery() -> str:
        with open('sqls/venda.sql', 'r') as file:
            return file.read()

    @staticmethod
    def transferConfig():
        database = {
            'from': 'sqlsrv',
            'to': 'pgsql'
        }

        return database
