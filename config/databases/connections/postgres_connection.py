import psycopg2
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
