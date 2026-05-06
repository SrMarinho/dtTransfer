# API: Driver

```python
from src.engine import Driver, register_driver, get_driver
```

## Base

```python
class Driver(ABC):
    @abstractmethod
    def connection(self, dbname, user=None, password=None, host=None, port=None): ...

    @abstractmethod
    def getCursor(self): ...

    def bulk_insert(self, conn, table: str, columns: list, rows: list) -> None:
        # default: executemany com placeholders ?
        ...

    @abstractmethod
    def insertValues(self): ...   # legacy hook
```

## Registry

```python
register_driver(name: str, cls: type) -> None
get_driver(name: str) -> Driver        # nova instância
list_drivers() -> list[str]
```

`register_driver` é idempotente para mesma classe; raise se outra classe registrada com mesmo nome.

## Built-in

| Nome | Classe | bulk_insert |
|------|--------|-------------|
| `pgsql`, `postgres` | `PostgresDB` | `COPY FROM` (StringIO + escape) |
| `sqlserver` | `SqlserverDB` | default executemany |
| `oracle` | `OracleDB` | default executemany |
| `sqlite` | `SqliteDB` | executemany com nomes de coluna |

## Resolução em workspaces

`workspace.yml` aceita driver names: `postgres`, `sqlserver`, `oracle`, `sqlite`, `fake`. `GenericDatabase` mapeia `postgres` → `pgsql` internamente para chamar `get_driver`.
