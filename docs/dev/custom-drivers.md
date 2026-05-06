# Driver custom

Adicione suporte a um banco novo (DuckDB, ClickHouse, MongoDB) sem editar o core.

## API

```python
from src.engine import Driver, register_driver


class DuckDBDriver(Driver):
    def connection(self, dbname, user=None, password=None, host=None, port=None):
        import duckdb
        self.connection = duckdb.connect(dbname)
        return self.connection

    def getCursor(self):
        return self.connection.cursor()

    def bulk_insert(self, conn, table: str, columns: list, rows: list) -> None:
        if not rows:
            return
        ph = ",".join(["?"] * len(columns))
        cur = conn.cursor()
        try:
            cur.executemany(f"INSERT INTO {table} VALUES ({ph})", rows)
            conn.commit()
        finally:
            cur.close()

    @staticmethod
    def insertValues(cur, sql, argslist, template=None, page_size=100, fetch=False):
        cur.executemany(sql, argslist)


register_driver("duckdb", DuckDBDriver)
```

## Quando registrar

Cedo no boot. Opções:
1. **Workspace `__init__.py`** (Python workspace) — chamado pelo loader
2. **Module side-effect** — em `src/plugins/duckdb_driver.py`, importado por `bootstrap` ou `run.py`
3. **Entry point** — futuro: `pyproject.toml [project.entry-points."datareplicator.drivers"]`

## Default `bulk_insert`

`Driver.bulk_insert` default usa `executemany` com placeholders `?`. Sobrescreva apenas se o driver tem path nativo (Postgres `COPY`, ClickHouse `INSERT FORMAT Native`).

## Usar no workspace

```yaml
target:
  name: dw
  driver: duckdb
  env_prefix: DB_DW
```

`get_driver("duckdb")` resolve para `DuckDBDriver`.
