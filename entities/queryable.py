from config.logger.logging import logger
from abc import ABC, abstractmethod

class Queryable(ABC):  # Classe abstrata Animal
    @staticmethod
    @abstractmethod
    def getQuery() -> str:
        ...

    def insert(self, rows):
        if(len(rows) == 0):
            logger.info("{self.tableName} - Sem dados para serem inseridos!")
            return

        try:
            conn = self.toDriver.connection()

            formatation = ['%s' for i in range(len(rows[0]))]
            
            query = f"INSERT INTO {self.tableName} VALUES ({','.join(formatation)});"

            cursor = conn.cursor()

            cursor.executemany(query, rows)

            conn.commit()

            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.info("{self.tableName} - Erro ao tentar inserir registro na tabela!")
    
    def existsTable(self):
        try:
            conn = self.toDriver.connection()
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (self.tableName,))
            res = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return res
        except Exception as e:
            logger.info(f"{self.tableName} - Erro ao tentar checkar se a tabela existe.")
    
    def truncate(self):
        try:
            
            conn = self.toDriver.connection()
            cursor = conn.cursor()

            cursor.execute(f"TRUNCATE TABLE {self.tableName};")

            conn.commit()

            cursor.close()
            conn.close()

            logger.info(f"{self.tableName} - O truncamento da tabela foi bem-sucedido.")
        except Exception as e:
            logger.info(f"Erro ao truncar tabela {self.tableName}.")
