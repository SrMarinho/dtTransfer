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

            logger.info(f"{table.name} - Inserindo dados...")
            while True:
                rows = fromCursor.fetchmany(init.ROWSNUM)
                if not rows:
                    break

                numOfRows += len(rows)

                table.insert(rows)

            fromCursor.close()
            fromConnection.close()
            
            endTime = time.time()
            totalTime = endTime - self.startTime
            
            logger.info(f"{table.name} - Processo finalizado com sucesso!")
            logger.debug(f"{table.name} - Foram inseridas {numOfRows} em {totalTime:.2f} segundo(s).")
            logger.debug(f"{table.name} - Velocidade de {(numOfRows / totalTime):.2f} itens por segundo.")
        except Exception as e:
            logger.info(f"{self.params['table']} - Erro! {e}")
