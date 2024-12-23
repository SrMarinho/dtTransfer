from datetime import *
from processes.process import Process
from factories.queryable_factory import QueryableFactory
from factories.database_factory import DatabaseFactory
from factories.database_driver_factory import DatabaseDriverFactory
import processes as init
import time
from config.logger.logging import logger

class nMonthsAgo(Process):
    def __init__(self, params):
        self.params = params
        self.insertedRows = 0
        self.start_time = time.time()
        self.months_list = []

    def oneMonth(self, table, originalQuery, currentMonth):
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
            nextMonth = (currentMonth.replace(day=28) + timedelta(days=4)).replace(day=1)

            table.deleteMonth(str(currentMonth), str(nextMonth))

            currentQuery = originalQuery.replace('REPLACE_START_DATE', str(currentMonth)).replace('REPLACE_END_DATE', str(nextMonth))
            
            fromCursor = connection.cursor()
            fromCursor.execute(currentQuery)
            
            # logger.debug(currentQuery)
            totalRows = 0

            logger.debug(f"{table.name} - Inserindo linhas na tabela no mes {currentMonth.strftime('%Y-%m')}...")
            while True:
                rows = fromCursor.fetchmany(init.ROWSNUM)
                if not rows:
                    break
                
                self.insertedRows += len(rows)
                totalRows += len(rows)

                table.insert(rows)
            
            connection.commit()
            
            logger.info(f"{table.name} - Numero de linhas inseridas na tabela no mes {currentMonth.strftime('%Y-%m')}: {str(totalRows)}")
            totalTime = time.time() - start_time
            logger.debug(f"{table.name} - Itens inseridos por segundo: {(totalRows / totalTime):.2f}")

            fromCursor.close()
            connection.close()
        except Exception as e:
            logger.debug(e)

    def run(self):
        table = QueryableFactory.getInstance(self.params['table'], self.params)
        originalQuery = table.getQuery()
        today = date.today()

        for month in range(int(self.params['months'])):
            first_day_of_month = (today.replace(day=1) - timedelta(days=month*30)).replace(day=1)
            self.months_list.append(first_day_of_month)

        for currentMonth in self.months_list:
            try:
                self.oneMonth(table, originalQuery, currentMonth)
            except Exception as e:
                logger.debug(e)

        end_time = time.time()
        totalTime = end_time - self.start_time

        logger.debug(f"{table.name} - Tempo de execução: {totalTime:.2f} segundos")
        logger.debug(f"{table.name} - Total de itens inseridos: {self.insertedRows} itens")
        logger.debug(f"{table.name} - Itens inseridos por segundo: {(self.insertedRows / totalTime):.2f}")
