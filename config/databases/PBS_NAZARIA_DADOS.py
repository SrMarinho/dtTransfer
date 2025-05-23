from config.logger.logging import logger
import os
from dotenv import load_dotenv
from config.databases.connections.postgres_connection import PostgresDB
from factories.database_driver_factory import DatabaseDriverFactory

load_dotenv()

class PbsNazariaDados():
    def __init__(self):
        self.driver = 'sqlserver'
        self.host = os.getenv("DB_NAZARIA_SQLSERVER_HOST")
        self.port = os.getenv("DB_NAZARIA_SQLSERVER_PORT")
        self.database = os.getenv("DB_NAZARIA_SQLSERVER_DATABASE")
        self.username = os.getenv("DB_NAZARIA_SQLSERVER_USERNAME")
        self.password = os.getenv("DB_NAZARIA_SQLSERVER_PASSWORD")
    
    def getDriver(self):
        return DatabaseDriverFactory.getInstance(self.driver)

    def connection(self):
        driver = self.getDriver()
        try:

            return driver.connection(
                        self.database,
                        self.username,
                        self.password,
                        self.host,
                        self.port
                    )
        except Exception as e:
            logger.info("Erro ao tentar conectar ao driver {} no banco {}".format(self.driver, self.database))
            raise e
    