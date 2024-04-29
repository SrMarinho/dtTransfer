import pyodbc
from config.databases.connections.database import Database

class SqlserverDB(Database):
    def __init__(self):    
        ...

    def connection(self, dbname, user, password, host='127.0.0.1', port='1433'):
        sql_server_conn = pyodbc.connect(
            """DRIVER={{ODBC Driver 17 for SQL Server}};
            SERVER={}, {};
            DATABASE={};
            UID={};
            PWD={};""".format(host, port, dbname, user, password)
        )
        return sql_server_conn

    def getCursor(self):
        return self.connection.cursor()
