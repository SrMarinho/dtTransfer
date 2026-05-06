import time
import threading
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from src.processes.process import Process, strip_date_filter
from src.processes.params import MonthlyParams
from src.processes.retry import connect_with_retry
from src.core.entity import Entity, filter_columns
from src.core.settings import BATCH_SIZE
from src.core.logger.logging import logger as _default_logger


def get_previous_months(start_date, num_months):
    months_list = []
    for month in range(num_months):
        current_date = start_date - relativedelta(months=month)
        current_date = current_date.replace(day=1)
        months_list.append(current_date)
    return months_list


class Monthly(Process):
    def __init__(
        self,
        table: Entity,
        params: MonthlyParams,
        on_progress=None,
        today_fn=date.today,
        logger=None,
        retry_base_delay: float = 30.0,
        retry_max_delay: float = 120.0,
    ):
        self.table = table
        self.params = params
        self.on_progress = on_progress
        self.today_fn = today_fn
        self._logger = logger or _default_logger
        self.insertedRows = 0
        self.start_time = time.time()
        self.months_list = []
        self._stop = threading.Event()
        self._retry_base_delay = retry_base_delay
        self._retry_max_delay = retry_max_delay

    def oneMonth(self, table, originalQuery, currentMonth):
        try:
            connection = connect_with_retry(
                table.fromDriver, table.name, self._stop,
                base_delay=self._retry_base_delay, max_delay=self._retry_max_delay,
            )
            if connection is None:
                return

            nextMonth = (currentMonth.replace(day=28) + timedelta(days=4)).replace(day=1)
            table.deleteMonth(str(currentMonth), str(nextMonth))

            currentQuery = originalQuery.replace('REPLACE_START_DATE', str(currentMonth)).replace('REPLACE_END_DATE', str(nextMonth))

            fromCursor = connection.cursor()
            fromCursor.execute(currentQuery)

            totalRows = 0
            self._logger.debug(f"{table.name} - Inserindo linhas na tabela no mes {currentMonth.strftime('%Y-%m')}...")
            start_time = time.time()
            while True:
                rows = fromCursor.fetchmany(BATCH_SIZE)
                if not rows:
                    break

                self.insertedRows += len(rows)
                totalRows += len(rows)
                table.insert(rows)

            connection.commit()

            self._logger.info(f"{table.name} - Numero de linhas inseridas na tabela no mes {currentMonth.strftime('%Y-%m')}: {str(totalRows)}")
            totalTime = time.time() - start_time
            rowsPerSecond = totalRows / totalTime if totalTime > 0 else 0
            self._logger.debug(f"{table.name} - Itens inseridos por segundo: {rowsPerSecond:.2f}")

            fromCursor.close()
            connection.close()
        except Exception as e:
            self._logger.debug(e)

    def _run_full(self, table, query):
        connection = connect_with_retry(
            table.fromDriver, table.name, self._stop,
            base_delay=self._retry_base_delay, max_delay=self._retry_max_delay,
        )
        if connection is None:
            return

        fromCursor = connection.cursor()
        fromCursor.execute(query)

        start_time = time.time()
        while True:
            rows = fromCursor.fetchmany(BATCH_SIZE)
            if not rows:
                break
            rows = filter_columns(table.columns, rows, fromCursor.description)
            self.insertedRows += len(rows)
            table.insert(rows)

        connection.commit()
        fromCursor.close()
        connection.close()

        totalTime = time.time() - start_time
        self._logger.info(f"{table.name} - Full load finalizado: {self.insertedRows} linhas em {totalTime:.2f}s")

    def byMonth(self):
        table = self.table
        today = self.today_fn()

        self.months_list = get_previous_months(today, self.params.months or 0)
        self.months_list = self.months_list[::-1]

        originalQuery = table.getQuery()

        for i, currentMonth in enumerate(self.months_list):
            try:
                self.oneMonth(table, originalQuery, currentMonth)
                if self.on_progress:
                    self.on_progress(current=i + 1, total=len(self.months_list))
            except Exception as e:
                self._logger.debug(e)

        end_time = time.time()
        totalTime = end_time - self.start_time

        self._logger.debug(f"{table.name} - Tempo de execução: {totalTime:.2f} segundos")
        self._logger.debug(f"{table.name} - Total de itens inseridos: {self.insertedRows} itens")
        if totalTime:
            self._logger.debug(f"{table.name} - Itens inseridos por segundo: {(self.insertedRows / totalTime):.2f}")

    def wholeInterval(self):
        table = self.table
        today = self.today_fn()

        months_list = get_previous_months(today, self.params.months or 0)
        start_date = months_list[-1]
        end_date = (today.replace(day=28) + timedelta(days=4)).replace(day=1)

        originalQuery = table.getQuery()

        try:
            connection = connect_with_retry(
                table.fromDriver, table.name, self._stop,
                base_delay=self._retry_base_delay, max_delay=self._retry_max_delay,
            )
            if connection is None:
                return

            start_time = time.time()
            table.deleteMonth(str(start_date), str(end_date))

            currentQuery = originalQuery.replace('REPLACE_START_DATE', str(start_date)) \
                                        .replace('REPLACE_END_DATE', str(end_date))

            fromCursor = connection.cursor()
            fromCursor.execute(currentQuery)

            totalRows = 0
            self._logger.debug(f"{table.name} - Inserindo linhas na tabela no intervalo {start_date} a {end_date}...")

            while True:
                rows = fromCursor.fetchmany(BATCH_SIZE)
                if not rows:
                    break

                rows = filter_columns(table.columns, rows, fromCursor.description)
                self.insertedRows += len(rows)
                totalRows += len(rows)
                table.insert(rows)

            connection.commit()

            self._logger.info(f"{table.name} - Número total de linhas inseridas: {str(totalRows)}")
            totalTime = time.time() - start_time
            if totalTime:
                self._logger.debug(f"{table.name} - Itens inseridos por segundo: {(totalRows / totalTime):.2f}")

            fromCursor.close()
            connection.close()
        except Exception as e:
            self._logger.error(f"Erro durante o processamento do intervalo completo: {str(e)}")
            raise

    def run(self):
        table = self.table
        p = self.params

        self._logger.info(f"{table.name} - Processo iniciado!")

        if p.truncate:
            table.truncate()

        if p.full:
            self._run_full(table, strip_date_filter(table.getQuery()))
            self._logger.info(f"{table.name} - Processo finalizado!")
            return

        processing_methods = {
            "byMonth": self.byMonth,
            "wholeInterval": self.wholeInterval,
        }

        selected_method = processing_methods.get(p.method, self.byMonth)
        selected_method()
