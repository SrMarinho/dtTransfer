import os
from dotenv import load_dotenv
from config.databases.connections.postgres_connection import PostgresDB
from factories.database_driver_factory import DatabaseDriverFactory

load_dotenv()

class BiMktNaz():
    def __init__(self):
        self.driver = 'pgsql'
        self.host = os.getenv("DB_BIMKTNAZ_POSTGRES_HOST")
        self.port = os.getenv("DB_BIMKTNAZ_POSTGRES_PORT")
        self.database = os.getenv("DB_BIMKTNAZ_POSTGRES_DATABASE")
        self.username = os.getenv("DB_BIMKTNAZ_POSTGRES_USERNAME")
        self.password = os.getenv("DB_BIMKTNAZ_POSTGRES_PASSWORD")

    def connection(self):
        driver = DatabaseDriverFactory.getInstance(self.driver)

        try:

            return driver.connection(
                        self.database,
                        self.username,
                        self.password,
                        self.host,
                        self.port
                    )
        except Exception as e:
            print("Erro ao tentar conectar ao driver {} no banco {}".format(self.driver, self.database))
            raise e
    
