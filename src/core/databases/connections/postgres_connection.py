from io import StringIO

import psycopg2
from psycopg2.extras import execute_values

from src.core.databases.connections.database import Database
from src.core.logger.logging import logger


class PostgresDB(Database):
    def __init__(self):
        ...

    def connection(self, dbname, user, password, host='127.0.0.1', port='5432'):
        self.connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            options="-c datestyle=ISO,DMY -c client_encoding=UTF8",
        )
        return self.connection

    def getCursor(self):
        return self.connection.cursor()

    def bulk_insert(self, conn, table: str, columns: list, rows: list) -> None:
        if not rows:
            return
        conn.autocommit = False
        sep = "|"
        expected = len(columns)
        buffer = StringIO()
        try:
            for row in rows:
                if len(row) != expected:
                    logger.error(f"{table} - linha com colunas != {expected}: {row}")
                    continue
                cleaned = []
                for v in row:
                    if v is None or v == "":
                        cleaned.append("\\N")
                    else:
                        s = (
                            str(v)
                            .replace("\\", "\\\\")
                            .replace("\r", "\\r")
                            .replace("\n", "\\n")
                            .replace(sep, "\\" + sep)
                        )
                        cleaned.append(s)
                buffer.write(sep.join(cleaned) + "\n")
            buffer.seek(0)
            cur = conn.cursor()
            try:
                cur.copy_from(file=buffer, table=table, sep=sep, columns=columns, null="\\N")
                conn.commit()
            finally:
                cur.close()
        finally:
            buffer.close()

    @staticmethod
    def insertValues(cur, sql, argslist, template=None, page_size: int = 100, fetch: bool = False):
        try:
            execute_values(cur, sql, argslist, template, page_size, fetch)
        except Exception as e:
            raise RuntimeError(f"Error in bulk execute: {str(e)}") from e
