import sqlite3

from src.core.databases.connections.database import Database


class SqliteDB(Database):
    def connection(self, dbname, user=None, password=None, host=None, port=None):
        self.connection = sqlite3.connect(dbname)
        return self.connection

    def getCursor(self):
        return self.connection.cursor()

    def bulk_insert(self, conn, table: str, columns: list, rows: list) -> None:
        if not rows:
            return
        ph = ",".join(["?"] * len(columns))
        col_list = ",".join(columns)
        cur = conn.cursor()
        try:
            cur.executemany(f"INSERT INTO {table} ({col_list}) VALUES ({ph})", rows)
            conn.commit()
        finally:
            cur.close()

    @staticmethod
    def insertValues(cur, sql, argslist, template=None, page_size=100, fetch=False):
        cur.executemany(sql, argslist)
