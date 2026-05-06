from src.core.logger.logging import logger
from src.factories.database_factory import DatabaseFactory
from pathlib import Path
from typing import Optional, Sequence


def filter_columns(columns: Sequence[str], rows: list, description) -> list:
    if not columns:
        return rows

    name_to_idx = {desc[0].lower(): i for i, desc in enumerate(description)}
    try:
        indices = [name_to_idx[c.lower()] for c in columns]
    except KeyError:
        # Fallback posicional: SQL retorna colunas na ordem declarada no YAML
        indices = list(range(len(columns)))

    return [[row[i] for i in indices] for row in rows]


class Entity:
    """Base class for all ETL entities."""

    def __init__(self, params):
        self.params = params
        self.fromDB = None
        self.toDB = None
        self._fromDriver = None
        self._toDriver = None
        self.name = None
        self.columns = []
        self.query_path = None
        self.incremental_column: Optional[str] = None

    @property
    def fromDriver(self):
        if not hasattr(self, '_fromDriver') or self._fromDriver is None:
            self._fromDriver = DatabaseFactory.getInstance(self.fromDB)
        return self._fromDriver

    @property
    def toDriver(self):
        if not hasattr(self, '_toDriver') or self._toDriver is None:
            self._toDriver = DatabaseFactory.getInstance(self.toDB)
        return self._toDriver

    def getQuery(self) -> str:
        if not self.name:
            raise ValueError("É necessario ter o nome da tabela")
        if not getattr(self, 'query_path', None):
            raise ValueError(f"{self.name} - query_path not set")
        with open(str(self.query_path), 'r', encoding='utf-8') as file:
            return file.read()

    def insert(self, rows):
        """Delegates to the target driver's bulk_insert."""
        if not rows:
            logger.info(f"{self.name} - Sem dados para serem inseridos!")
            return
        try:
            conn = self.toDriver.connection()
            driver = self.toDriver.getDriver()
            driver.bulk_insert(conn, self.name, self.columns, rows)
        except Exception as e:
            logger.error(f"{self.name} - Erro ao inserir dados: {e}")
            raise
        finally:
            try:
                conn.close()
            except Exception:
                ...

    def existsTable(self):
        try:
            conn = self.toDriver.connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
                (self.name,),
            )
            res = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return res
        except Exception as e:
            logger.debug(f"{self.name} - existsTable fallback: {e}")
            return False

    def truncate(self):
        try:
            conn = self.toDriver.connection()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.name}")
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"{self.name} - Truncado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao truncar tabela {self.name}: {e}")

    def _delete_range(self, startDate: str, endDate: str) -> None:
        col = self.incremental_column
        if not col:
            return
        try:
            conn = self.toDriver.connection()
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM {self.name} WHERE {col} >= %s AND {col} < %s",
                (startDate, endDate),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"{self.name} - Erro ao deletar dados ({startDate}..{endDate}): {e}")

    def deleteDay(self, startDate: str, endDate: str) -> None:
        self._delete_range(startDate, endDate)

    def deleteMonth(self, startDate: str, endDate: str) -> None:
        self._delete_range(startDate, endDate)

    def createTable(self):
        ...
