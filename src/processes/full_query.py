import time
from src.processes.process import Process
from src.processes.params import FullQueryParams
from src.core.entity import Entity, filter_columns
from src.core.settings import BATCH_SIZE
from src.core.logger.logging import logger as _default_logger


class FullQuery(Process):
    def __init__(self, table: Entity, params: FullQueryParams, logger=None):
        self.table = table
        self.params = params
        self._logger = logger or _default_logger
        self.insertedRows = 0

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
        table = self.table
        try:
            self._logger.info(f"{table.name} - Processo iniciado!")

            originalQuery = table.getQuery()

            fromConnection = table.fromDriver.connection()
            fromCursor = fromConnection.cursor()
            fromCursor.execute(originalQuery)

            if self.params.truncate:
                table.truncate()

            numOfRows = 0
            sizeInMB = 0
            self._logger.info(f"{table.name} - Inserindo dados...")
            startTime = time.time()
            while True:
                rows = fromCursor.fetchmany(BATCH_SIZE)
                if not rows:
                    break

                rows = filter_columns(table.columns, rows, fromCursor.description)
                sizeInMB += self.calculateSize(rows)
                numOfRows += len(rows)
                table.insert(rows)

            fromCursor.close()
            fromConnection.close()

            endTime = time.time()
            totalTime = endTime - startTime

            self._logger.info(f"{table.name} - Processo finalizado com sucesso!")
            self._logger.info(f"{table.name} - Foram inseridas {numOfRows} em {totalTime:.2f} segundo(s).")
            if not totalTime:
                self._logger.debug(f"{table.name} - Velocidade de 0 itens por segundo.")
            else:
                self._logger.debug(f"{table.name} - Velocidade de {(numOfRows / totalTime):.2f} itens por segundo.")
            self._logger.debug(f"{table.name} - Tamanho dos dados: {sizeInMB:.2f}MB")
            return True
        except Exception as e:
            self._logger.error(f"{table.name} - {e}")
            raise e
