from config.logger.logging import logger
from config.databases.connections.database import Database
import oracledb

class OracleDB(Database):
    def __init__(self):    
        ...

    def connection(self, serviceName, user, password, host='127.0.0.1', port='1521', encoding = 'utf8'):
        try:
            oracledb.init_oracle_client()
        except Exception as e:
            ...
        
        try:
            return  oracledb.connect(user = user, password = password, host = host, port = port, service_name = serviceName)
        except Exception as e:
            logger.info("Erro ao tentar criar conexão com banco de dados oracle host '{}' na porta '{}'!".format(host, port))
            raise e

    def getCursor(self):
        return self.connection.cursor()
    
    @staticmethod
    def insertValues(cur, sql, argslist, template = None, page_size: int = 100, fetch: bool = False):
        raise NotImplementedError(f"Metodo de inserção para {__name__}")