from datetime import datetime, date, timedelta
from processes.process import Process
from factories.queryable_factory import QueryableFactory
from factories.database_factory import DatabaseFactory
from factories.database_driver_factory import DatabaseDriverFactory
import processes as init
import time
from config.logger.logging import logger

def get_previous_months(start_date, num_months):
    months_list = []
    for i in range(num_months):
        if start_date.month - i > 0:
            year = start_date.year
            month = start_date.month - i
        else:
            year = start_date.year - 1
            month = 12 + (start_date.month - i)
        first_day_of_month = date(year, month, 1)
        months_list.append(first_day_of_month)
    return months_list

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
    
    def byMonth(self):
        table = QueryableFactory.getInstance(self.params['table'], self.params)
        originalQuery = table.getQuery()
        today = date.today()

        # Calcula os meses anteriores manualmente
        self.months_list = get_previous_months(today, int(self.params['months']))
        self.months_list = self.months_list[::-1]

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

    def wholeInterval(self):
        table = QueryableFactory.getInstance(self.params['table'], self.params)
        originalQuery = table.getQuery()
        
        # Calcula o intervalo completo baseado nos meses solicitados
        today = date.today()
        months_list = get_previous_months(today, int(self.params['months']))
        start_date = months_list[-1]  # O mês mais antigo
        end_date = (today.replace(day=28) + timedelta(days=4)).replace(day=1)  # Primeiro dia do próximo mês
        
        tries = 0
        try:
            connection = None
            while connection is None:
                try:
                    connection = table.fromDriver.connection()
                except Exception as e:
                    tries += 1
                    time.sleep(30 * tries)
                    logger.warning(f"{table.name} - Erro ao tentar criar conexão, tentando novamente em {30 * tries} segundos")

            start_time = time.time()
            
            table.deleteMonth(str(start_date), str(end_date))
            
            currentQuery = originalQuery.replace('REPLACE_START_DATE', str(start_date)) \
                                    .replace('REPLACE_END_DATE', str(end_date))
            
            fromCursor = connection.cursor()
            fromCursor.execute(currentQuery)
            
            totalRows = 0
            logger.debug(f"{table.name} - Inserindo linhas na tabela no intervalo {start_date} a {end_date}...")
            
            while True:
                rows = fromCursor.fetchmany(init.ROWSNUM)
                if not rows:
                    break
                
                self.insertedRows += len(rows)
                totalRows += len(rows)
                table.insert(rows)
            
            connection.commit()
            
            logger.info(f"{table.name} - Número total de linhas inseridas: {str(totalRows)}")
            totalTime = time.time() - start_time
            logger.debug(f"{table.name} - Itens inseridos por segundo: {(totalRows / totalTime):.2f}")

            fromCursor.close()
            connection.close()
        except Exception as e:
            logger.error(f"Erro durante o processamento do intervalo completo: {str(e)}")
            raise

    def run(self):
        processing_methods = {
            "byMonth": self.byMonth,
            "wholeInterval": self.wholeInterval,
        }

        selected_method = processing_methods['byMonth']
        if 'method' in self.params:
            if self.params['method'] in processing_methods:
                selected_method = processing_methods[self.params['method']]
            
        selected_method()