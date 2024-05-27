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
            tableInstance = QueryableFactory.getInstance(self.params['table'], self.params)

            originalQuery = tableInstance.getQuery()
            

            fromConnection = tableInstance.fromDriver.connection()

            fromCursor = fromConnection.cursor()
            fromCursor.execute(originalQuery)
            

            if "truncate" in self.params:
                if self.params["truncate"]: tableInstance.truncate()

            numOfRows = 0

            while True:
                rows = fromCursor.fetchmany(init.ROWSNUM)
                if not rows:
                    break

                numOfRows += len(rows)

                tableInstance.insert(rows)

            fromCursor.close()
            fromConnection.close()
            
            endTime = time.time()
            totalTime = endTime - self.startTime
            
            logger.debug(f"Foram inseridas {numOfRows} em {totalTime:.2f} segundo(s).")
            logger.debug(f"Velocidade de {(numOfRows / totalTime):.2f} itens por segundo.")
        except Exception as e:
            logger.debug(e)
