import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from src.processes.process import Process, strip_date_filter
from src.processes.params import IncrementalParams
from src.processes.retry import connect_with_retry
from src.core.entity import Entity, filter_columns
from src.core.settings import BATCH_SIZE, THREADS_NUM
from src.core.logger.logging import logger as _default_logger


class Incremental(Process):
    def __init__(
        self,
        table: Entity,
        params: IncrementalParams,
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
        self._total_days = 0
        self._completed_days = 0
        self.lock = threading.Lock()
        self._stop = threading.Event()
        self._retry_base_delay = retry_base_delay
        self._retry_max_delay = retry_max_delay

    def oneDay(self, table, originalQuery, currentDay):
        try:
            connection = connect_with_retry(
                table.fromDriver, table.name, self._stop,
                base_delay=self._retry_base_delay, max_delay=self._retry_max_delay,
            )
            if connection is None:
                return

            nextDay = currentDay + timedelta(days=1)

            self._logger.debug(currentDay)
            table.deleteDay(str(currentDay), str(nextDay))

            currentQuery = originalQuery.replace('REPLACE_START_DATE', str(currentDay)).replace('REPLACE_END_DATE', str(nextDay))

            fromCursor = connection.cursor()
            fromCursor.execute(currentQuery)

            totalRows = 0
            self._logger.debug(f"{table.name} - Inserindo linhas na tabela no dia {currentDay}...")
            start_time = time.time()
            while True:
                rows = fromCursor.fetchmany(BATCH_SIZE)
                if not rows:
                    break

                rows = filter_columns(table.columns, rows, fromCursor.description)
                with self.lock:
                    self.insertedRows += len(rows)
                totalRows += len(rows)
                table.insert(rows)

            connection.commit()

            self._logger.info(f"{table.name} - Numero de linhas inseridas na tabela no dia {currentDay}: {str(totalRows)}")
            totalTime = time.time() - start_time
            if not totalTime:
                self._logger.debug(f"{table.name} - Itens inseridos por segundo: 0")
            else:
                self._logger.debug(f"{table.name} - Itens inseridos por segundo: {(totalRows / totalTime):.2f}")

            fromCursor.close()
            connection.close()
        except Exception as e:
            self._logger.error(f"{table.name} - {str(e)}")

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

    def run(self):
        table = self.table
        p = self.params

        self._logger.info(f"{table.name} - Processo iniciado!")

        originalQuery = table.getQuery()

        if p.truncate:
            table.truncate()

        if p.full:
            self._run_full(table, strip_date_filter(originalQuery))
            self._logger.info(f"{table.name} - Processo finalizado!")
            return

        today = self.today_fn()

        current_day_offset = 0 if p.current_day else 1
        days_list = [
            today - timedelta(days=i + current_day_offset)
            for i in range(p.days or 0)
        ]

        self._total_days = len(days_list)
        threads_num = p.threads if p.threads else THREADS_NUM

        with ThreadPoolExecutor(max_workers=threads_num) as executor:
            futures = {
                executor.submit(self.oneDay, table, originalQuery, day): day
                for day in days_list
            }
            for future in as_completed(futures):
                future.result()
                with self.lock:
                    self._completed_days += 1
                    completed = self._completed_days
                if self.on_progress:
                    self.on_progress(current=completed, total=self._total_days)

        end_time = time.time()
        totalTime = end_time - self.start_time

        self._logger.info(f"{table.name} - Processo finalizado!")
        self._logger.debug(f"{table.name} - Tempo de execução: {totalTime:.2f} segundos")
        self._logger.info(f"{table.name} - Total de itens inseridos: {self.insertedRows} itens")
        if not totalTime:
            self._logger.debug(f"{table.name} - Itens inseridos por segundo: 0")
        else:
            self._logger.debug(f"{table.name} - Itens inseridos por segundo: {(self.insertedRows / totalTime):.2f}")
