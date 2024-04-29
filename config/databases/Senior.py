
import os
from dotenv import load_dotenv
from config.databases.connections.oracle_connection import OracleDB
from factories.database_driver_factory import DatabaseDriverFactory

load_dotenv()

class Senior():
    def __init__(self):
        self.driver = 'oracle'
        self.serviceName = os.getenv("DB_SENIOR_ORACLE_SERVICE_NAME")
        self.host = os.getenv("DB_SENIOR_ORACLE_HOST")
        self.port = os.getenv("DB_SENIOR_ORACLE_PORT")
        self.username = os.getenv("DB_SENIOR_ORACLE_USER")
        self.password = os.getenv("DB_SENIOR_ORACLE_PASSWORD")
        self.encoding = os.getenv("DB_SENIOR_ORACLE_ENCODING")
    
    def connection(self):
        driver = DatabaseDriverFactory.getInstance(self.driver)
        
        try:
            return driver.connection(
                        self.serviceName,
                        self.username,
                        self.password,
                        self.host,
                        self.port,
                        self.encoding
                    )
        except Exception as e:
            print("Erro ao tentar conectar ao driver {} no banco {}".format(self.driver, self.serviceName))
            raise e
