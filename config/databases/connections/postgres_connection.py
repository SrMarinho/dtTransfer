import psycopg2
from psycopg2.extras import execute_values
from config.databases.connections.database import Database

class PostgresDB(Database):
    def __init__(self):    
        ...

    def connection(self, dbname, user, password, host='127.0.0.1', port='5432'):
        self.connection = psycopg2.connect(
            dbname   = dbname,
            user     = user,
            password = password,
            host     = host,
            port     = port
        )

        return self.connection
    
    def getCursor(self):
        return self.connection.cursor()

    @staticmethod
    def insertValues(cur, sql, argslist, template = None, page_size: int = 100, fetch: bool = False):
        try:
            execute_values(cur, sql, argslist, template, page_size, fetch)
        except Exception as e:
            raise RuntimeError(f"Error in bulk execute: {str(e)}") from e