from src.core.logger.logging import logger

class FakeDatabaseDriver:
    def __init__(self, database=None, host=None, user=None, password=None):
        """Inicializa o driver fake com parâmetros de conexão"""
        self.name = 'FakeDatabase'
        self.database = database
        self.host = host
        self.user = user
        self.password = password
        self.connected = False
        self.transaction_open = False
        
    def connect(self):
        """Simula a conexão com o banco de dados"""
        if not self.connected:
            self.connected = True
            return True
        return False
    
    def disconnect(self):
        """Simula a desconexão do banco de dados"""
        if self.connected:
            self.connected = False
            return True
        return False
    
    def connection(self):
        """Retorna o objeto de conexão fake"""
        if not self.connected:
            self.connect()
            
        class FakeConnection:
            def __init__(self, driver):
                self.driver = driver
                
            def cursor(self):
                """Retorna um cursor fake"""
                class FakeCursor:
                    def __init__(self, connection):
                        self.connection = connection
                        self.description = None
                        self.rowcount = 0
                        self.closed = False
                        self.results = []
                        self.arraysize = 1  # Tamanho padrão para fetchmany
                        
                    def execute(self, query, params=None):
                        """Simula a execução de uma query"""
                        logger.debug(f"Fake: Executando query: {query}")
                        if params:
                            logger.debug(f"Com parâmetros: {params}")
                        # Simula resultados para SELECT
                        if query.strip().upper().startswith("SELECT"):
                            self.results = [("dado1", 1), ("dado2", 2), ("dado3", 3), 
                                          ("dado4", 4), ("dado5", 5)]
                            self.rowcount = len(self.results)
                            self.description = [("col1",), ("col2",)]
                        # Simula resultados para INSERT/UPDATE/DELETE
                        else:
                            self.rowcount = 1
                        return True
                        
                    def fetchone(self):
                        """Retorna uma linha do resultado"""
                        if self.results:
                            return self.results.pop(0)
                        return None
                        
                    def fetchmany(self, size=None):
                        """
                        Retorna um número especificado de linhas
                        Se size não for especificado, usa o valor de arraysize
                        """
                        if size is None:
                            size = self.arraysize
                            
                        results = []
                        for _ in range(min(size, len(self.results))):
                            results.append(self.results.pop(0))
                        return results
                        
                    def fetchall(self):
                        """Retorna todas as linhas do resultado"""
                        results = self.results
                        self.results = []
                        return results
                        
                    def close(self):
                        """Fecha o cursor"""
                        self.closed = True
                        
                    def setinputsizes(self, sizes):
                        """Método opcional para definir tamanhos de parâmetros"""
                        pass
                        
                    def setoutputsize(self, size, column=None):
                        """Método opcional para definir tamanho de saída"""
                        pass
                        
                    def __enter__(self):
                        return self
                        
                    def __exit__(self, exc_type, exc_val, exc_tb):
                        self.close()
                        
                return FakeCursor(self)
                
            def commit(self):
                """Simula commit de transação"""
                logger.debug("fake: Commit realizado")
                self.driver.transaction_open = False
                return True
                
            def rollback(self):
                """Simula rollback de transação"""
                logger.debug("fake: Rollback realizado")
                self.driver.transaction_open = False
                return True
                
            def close(self):
                """Fecha a conexão"""
                return self.driver.disconnect()
                
            def __enter__(self):
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.driver.transaction_open:
                    if exc_type is not None:  # Se houve exceção
                        self.rollback()
                    else:
                        self.commit()
                self.close()
                
        return FakeConnection(self)
    
    def __enter__(self):
        """Suporte para context manager"""
        self.connect()
        return self.connection()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante que a conexão será fechada ao sair do contexto"""
        self.disconnect()