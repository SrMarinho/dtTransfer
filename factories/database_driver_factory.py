from config.databases.connections.postgres_connection import PostgresDB
from config.databases.connections.sqlserver_connection import SqlserverDB
from config.databases.connections.oracle_connection import OracleDB

class DatabaseDriverFactory:
    @staticmethod
    def getInstance(name):
        driver_instances = {
            'pgsql': PostgresDB,
            'sqlserver': SqlserverDB,
            'oracle': OracleDB
        }

        if name in driver_instances:
            return driver_instances[name]()
        
        raise "Driver não encontrado!"
