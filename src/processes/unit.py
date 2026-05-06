import time
from src.processes.process import Process
from src.processes.params import UnitParams
from src.core.entity import Entity, filter_columns
from src.core.settings import BATCH_SIZE
from src.core.logger.logging import logger as _default_logger


class Unit(Process):
    def __init__(self, table: Entity, params: UnitParams, logger=None):
        self.table = table
        self.params = params
        self._logger = logger or _default_logger
        self.insertedRows = 0

    def _oneUnit(self, table: Entity, unit: int):
        with table.fromDriver.connection() as fromConnection:
            self._insertion(fromConnection, table, unit)
            fromConnection.commit()

    def _insertion(self, connection, table: Entity, unit: int):
        self._logger.info(f"{table.name} - Inserindo linhas na tabela da unidade {unit}...")
        with connection.cursor() as cursor:
            query = str(table.getQuery()).replace('REPLACE_UNIT_HERE', str(unit))
            cursor.execute(query)
            while True:
                rows = cursor.fetchmany(BATCH_SIZE)
                if not rows:
                    break
                rows = filter_columns(table.columns, rows, cursor.description)
                try:
                    table.insert(rows)
                except Exception as e:
                    self._logger.info(e)
                else:
                    self.insertedRows += len(rows)

    def run(self):
        table = self.table
        unit = self.params.unit

        start_time = time.time()

        try:
            self._oneUnit(table, unit)
        except Exception as e:
            self._logger.error(f"{table.name} - {e}")
            raise e

        end_time = time.time()
        totalTime = end_time - start_time

        self._logger.info(f"{table.name} - Processo finalizado!")
        self._logger.debug(f"{table.name} - Tempo de execução: {totalTime:.2f} segundos")
        self._logger.debug(f"{table.name} - Total de itens inseridos: {self.insertedRows} itens")
        if totalTime:
            self._logger.debug(f"{table.name} - Itens inseridos por segundo: {(self.insertedRows / totalTime):.2f}")
        else:
            self._logger.debug(f"{table.name} - Itens inseridos por segundo: 0")
