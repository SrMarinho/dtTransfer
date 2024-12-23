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
        self.days_list = []
        self.lock = threading.Lock()

    def oneDay(self, table, originalQuery, currentDay):
        tries = 0
        try:
            connection = None
            while connection is None:
                try:
                    connection = table.fromDriver.connection()
                except Exception as e:
                    tries += 1
                    time.sleep(30 * tries)
                    logger.warning(f"{table.name} - Erro ao tentar criar conexao, tentando novamente em {30 * tries} segundos")

            start_time = time.time()
            nextDay = currentDay + timedelta(days=1)

            logger.debug(currentDay)

            table.deleteDay(str(currentDay), str(nextDay))

            currentQuery = originalQuery.replace('REPLACE_START_DATE', str(currentDay)).replace('REPLACE_END_DATE', str(nextDay))

            fromCursor = connection.cursor()
            fromCursor.execute(currentQuery)
            
            totalRows = 0

            logger.debug(f"{table.name} - Inserindo linhas na tabela no dia {currentDay}...")
            while True:
                rows = fromCursor.fetchmany(init.ROWSNUM)
                if not rows:
                    break
                
                with self.lock:
                    self.insertedRows += len(rows)
                totalRows += len(rows)

                table.insert(rows)
            
            connection.commit()
            
            logger.info(f"{table.name} - Numero de linhas inseridas na tabela no dia {currentDay}: {str(totalRows)}")
            totalTime = time.time() - start_time
            logger.debug(f"{table.name} - Itens inseridos por segundo: {(totalRows / totalTime):.2f}")

            fromCursor.close()
            connection.close()
        except Exception as e:
            logger.info(e)

    def get_next_day(self):
        with self.lock:
            if self.days_list:
                return self.days_list.pop(0)
            else:
                return None

    def worker(self, table, originalQuery):
        while True:
            currentDay = self.get_next_day()
            if currentDay is None:
                break
            try:
                self.oneDay(table, originalQuery, currentDay)
            except Exception as e:
                logger.debug(e)

    def run(self):
        table = QueryableFactory.getInstance(self.params['table'], self.params)

        logger.info(f"{table.name} - Processo iniciado!")

        originalQuery = table.getQuery()
        today = date.today()
        
        
        if "truncate" in self.params:
            if self.params["truncate"]: table.truncate()
        
        currentDay = 1
        if 'currentDay' in self.params:
            try:
                if self.params['currentDay'].lower() == 'true': currentDay = 0
            except Exception as e:
                logger.info(f"{table.name} - Erro no parametro 'currentDay'. Coloque um valor booleano [True/False]")
                logger.info(f"{table.name} - {e}")

        
        for day in range(int(self.params['days'])):
            dayToProcess = today - timedelta(days=day + currentDay)
            self.days_list.append(dayToProcess)
        
        threadsNum = init.THREADSNUM
        if('threads' in self.params):
            try:
                threadsNum = int(self.params['threads'])
            except Exception as e:
                logger.debug(f"{table.name} - O valor em threads deve ser um inteiro.")

        threads = []
        for _ in range(threadsNum):
            thread = threading.Thread(target=self.worker, args=(table, originalQuery))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        totalTime = end_time - self.start_time

        logger.info(f"{table.name} - Processo finalizado!")
        logger.debug(f"{table.name} - Tempo de execução: {totalTime:.2f} segundos")
        logger.debug(f"{table.name} - Total de itens inseridos: {self.insertedRows} itens")
        logger.debug(f"{table.name} - Itens inseridos por segundo: {(self.insertedRows / totalTime):.2f}")
