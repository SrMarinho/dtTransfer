import pyodbc
from config.databases.connections.database import Database

class SqlserverDB(Database):
    def __init__(self):    
        ...

    def connection(self, dbname, user, password, host='127.0.0.1', port='1433'):
        sql_server_conn = pyodbc.connect(
            f"""DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={host}, {port};
            DATABASE={dbname};
            UID={user};
            PWD={password};"""
        )
        return sql_server_conn

    def getCursor(self):
        return self.connection.cursor()
    
    @staticmethod
    def insertValues(cur, sql, argslist, template = None, page_size: int = 100, fetch: bool = False):
        raise NotImplementedError(f"Metodo de inserção para {__name__}")