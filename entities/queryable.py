from abc import ABC, abstractmethod

class Queryable(ABC):  # Classe abstrata Animal
    @staticmethod
    @abstractmethod
    def getQuery() -> str:
        ...

    def insert(self, rows):
        if(len(rows) == 0):
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
            print("Erro ao tentar inserir registro da tabela {}!".format(self.tableName))
            print(e)
            raise e
    
    def existsTable(self):
        try:
            conn = self.toDriver.connection()
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (self.tableName,))
            res = cursor.fetchone()[0]
            cursor.close()
            return res
        except Exception as e:
            raise e
        
