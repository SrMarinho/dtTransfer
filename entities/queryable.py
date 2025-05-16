from config.logger.logging import logger
from abc import ABC, abstractmethod
from io import StringIO

class Queryable(ABC):
    @staticmethod
    @abstractmethod
    def getQuery() -> str:
        ...

    def insert(self, rows):
        if len(rows) == 0:
            logger.info(f"{self.name} - Sem dados para serem inseridos!")
            return

        try:
            conn = self.toDriver.connection()
            conn.autocommit = False
            cursor = conn.cursor()

            buffer = StringIO()
            expected_columns = len(self.columns)
            separator = "|"  # Separador único

            for i, row in enumerate(rows):
                if len(row) != expected_columns:
                    logger.error(f"{self.name} - Linha com mais colunas do que esperado:\n{row}")
                    continue  # Pula linhas com número errado de colunas

                cleaned_row = []
                for value in row:
                    if value is None or value == '':
                        cleaned_row.append("\\N")
                    else:
                        # Escapa \r, \n, | e agora também \
                        str_value = str(value).replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n").replace("|", "\\|")
                        cleaned_row.append(str_value)
                line = separator.join(cleaned_row)
                buffer.write(line + "\n")
            
            buffer.seek(0)
            cursor.copy_from(
                file=buffer,
                table=self.name,
                sep=separator,
                columns=self.columns,
                null="\\N"
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            # conn.rollback()
            logger.error(f"{self.name} - Erro ao inserir dados: {e}")
            raise
        finally:
            buffer.close()
    
    def existsTable(self):
        try:
            conn = self.toDriver.connection()
            cursor = conn.cursor()

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (self.name,))
            res = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return res
        except Exception as e:
            logger.info(f"{self.name} - Erro ao tentar checkar se a tabela existe.")
    
    def truncate(self):
        try:
            
            conn = self.toDriver.connection()
            cursor = conn.cursor()

            cursor.execute(f"TRUNCATE TABLE {self.name};")

            conn.commit()

            cursor.close()
            conn.close()

            logger.info(f"{self.name} - O truncamento da tabela foi bem-sucedido.")
        except Exception as e:
            logger.info(f"Erro ao truncar tabela {self.name}.")

    def deleteDay(self, startDate, endDate):
        ...

    
    def createTable(self):
        ...