import pyodbc
from src.core.databases.connections.database import Database

_DRIVERS = pyodbc.drivers()
_SQL_DRIVER = next(
    (d for d in _DRIVERS if d.startswith("ODBC Driver") and "SQL Server" in d),
    _DRIVERS[0] if any(d == "SQL Server" for d in _DRIVERS) else "SQL Server",
)


class SqlserverDB(Database):
    def __init__(self):    
        ...

    def connection(self, dbname, user, password, host='127.0.0.1', port='1433'):
        server = f"{host},{port}" if port else host
        conn_str = (
            f"DRIVER={{{_SQL_DRIVER}}};"
            f"SERVER={server};"
            f"DATABASE={dbname};"
            f"UID={user};"
            f"PWD={password};"
        )
        if _SQL_DRIVER.startswith("ODBC Driver"):
            conn_str += "TrustServerCertificate=yes;"
        sql_server_conn = pyodbc.connect(conn_str)
        return sql_server_conn

    def getCursor(self):
        return self.connection.cursor()
    
    @staticmethod
    def insertValues(cur, sql, argslist, template = None, page_size: int = 100, fetch: bool = False):
        raise NotImplementedError(f"Metodo de inserção para {__name__}")