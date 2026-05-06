from abc import ABC, abstractmethod


class Database(ABC):
    """Base driver interface.

    `connection()` opens and returns a DB-API connection.
    `bulk_insert()` writes many rows efficiently. Each driver picks the
    optimal path (COPY FROM, executemany, etc.).
    """

    @abstractmethod
    def connection(self):
        raise NotImplementedError()

    @abstractmethod
    def getCursor(self):
        raise NotImplementedError()

    def bulk_insert(self, conn, table: str, columns: list, rows: list) -> None:
        """Default: executemany. Override in driver for engine-native bulk."""
        if not rows:
            return
        ph = ",".join(["?"] * len(columns))
        cur = conn.cursor()
        try:
            cur.executemany(f"INSERT INTO {table} VALUES ({ph})", rows)
            conn.commit()
        finally:
            cur.close()

    @abstractmethod
    def insertValues(self):
        raise NotImplementedError()
