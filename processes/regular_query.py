from datetime import *
from processes.process import Process
from factories.queryable_factory import QueryableFactory
from factories.database_factory import DatabaseFactory
from factories.database_driver_factory import DatabaseDriverFactory
import processes as init
import time
from config.logger.logging import logger

class RegularQuery(Process):
    def __init__(self, params):
        self.params = params
        self.insertedRows = 0
        self.startTime = time.time()

    def calculateSize(self, rows):
        total_bytes = 0
        for row in rows:
            cleaned_row = [
                "\\N" if value is None else str(value).replace("\r", "\\r").replace("\n", "\\n")
                for value in row
            ]
            line = ";".join(cleaned_row) + "\n"
            total_bytes += len(line.encode('utf-8'))
        
        tamanho_mb = (total_bytes / 1024) / 1024 if rows else 0
        return tamanho_mb

    def run(self):
        try:
            table = QueryableFactory.getInstance(self.params['table'], self.params)

            logger.info(f"{table.name} - Processo iniciado!")

            originalQuery = table.getQuery()

            fromConnection = table.fromDriver.connection()

            fromCursor = fromConnection.cursor()
            fromCursor.execute(originalQuery)

            if "truncate" in self.params:
                if self.params["truncate"]: table.truncate()

            numOfRows = 0

            sizeInMB = 0
            logger.info(f"{table.name} - Inserindo dados...")
            while True:
                rows = fromCursor.fetchmany(init.ROWSNUM)
                if not rows:
                    break
                
                sizeInMB += self.calculateSize(rows)
                numOfRows += len(rows)

                table.insert(rows)

            fromCursor.close()
            fromConnection.close()
            
            endTime = time.time()
            totalTime = endTime - self.startTime
            
            logger.info(f"{table.name} - Processo finalizado com sucesso!")
            logger.debug(f"{table.name} - Foram inseridas {numOfRows} em {totalTime:.2f} segundo(s).")
            logger.debug(f"{table.name} - Velocidade de {(numOfRows / totalTime):.2f} itens por segundo.")
            logger.info(f"{table.name} - Tamanho dos dados: {sizeInMB:.2f}MB")
        except Exception as e:
            logger.info(f"{self.params['table']} - Erro! {e}")
