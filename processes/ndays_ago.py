from datetime import *
from processes.process import Process
from factories.queryable_factory import QueryableFactory
from factories.database_factory import DatabaseFactory
from factories.database_driver_factory import DatabaseDriverFactory
import processes as init
import time
import threading
from config.logger.logging import logger

class nDaysAgo(Process):
    def __init__(self, params):
        self.params = params
        self.insertedRows = 0
        self.start_time = time.time()

    def oneDay(self, tableInstance, originalQuery, today, nday):
        tries = 0
        try:
            connection = None
            while connection == None:
                try:
                    connection = tableInstance.fromDriver.connection()
                except Exception as e:
                    tries += 1
                    time.sleep(30 * tries)

                    logger.warning(f"{tableInstance.tableName} - Erro ao tentar criar conexao, tentando novamente em {30 * tries} segundos")
                    
            start_time = time.time()
            currentDay = today - timedelta(days=nday)
            nextDay = currentDay + timedelta(days=1)

            logger.debug(currentDay)

            tableInstance.deleteDay(str(currentDay), str(nextDay))

            currentQuery = originalQuery.replace('REPLACE_START_DATE', str(currentDay)).replace('REPLACE_END_DATE', str(nextDay))
            
            fromCursor = connection.cursor()
            fromCursor.execute(currentQuery)
            
            totalRows = 0

            while True:
                rows = fromCursor.fetchmany(init.ROWSNUM)
                if not rows:
                    break
                
                self.insertedRows += len(rows)
                totalRows += len(rows)

                tableInstance.insert(rows)
            
            logger.debug(f"{tableInstance.tableName} - Numero de linhas inseridas na tabela {tableInstance.tableName} no dia {currentDay}: {str(totalRows)}")
            totalTime = time.time() - start_time
            logger.debug(f"{tableInstance.tableName} - Itens inseridos por segundo: {(totalRows / totalTime):.2f}")

            fromCursor.close()
            connection.close()
        except Exception as e:
            logger.debug(e)

    def executeDays(self, tableInstance, originalQuery, start, days):
        for day in range(days):
            try:
                self.oneDay(tableInstance, originalQuery, start, day)
            except Exception as e:
                logger.debug(e)
    
    def run(self):
        tableInstance = QueryableFactory.getInstance(self.params['table'], self.params)

        originalQuery = tableInstance.getQuery()

        today = date.today()
        
        daysPerThread = 1

        if int(self.params['days']) > init.THREADSNUM:
            daysPerThread = (int(self.params['days'])) // init.THREADSNUM

        threads = []
        for day in range(0, int(self.params['days']), daysPerThread):
            currentDay = today - timedelta(days=day + 1)
            thread = threading.Thread(target=self.executeDays, args=(tableInstance, originalQuery, currentDay, daysPerThread))
            threads.append(thread)
            time.sleep(1)
            thread.start()

        for th in threads:
            th.join()

        end_time = time.time()
        totalTime = end_time - self.start_time

        logger.info(f"{tableInstance.tableName} - Tempo de execução: {totalTime:.2f} segundos")
        logger.info(f"{tableInstance.tableName} - Total de itens inseridos: {self.insertedRows} itens")
        logger.info(f"{tableInstance.tableName} - Itens inseridos por segundo: {(self.insertedRows / totalTime):.2f}")

