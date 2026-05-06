"""Driver API + plug-in registry.

Built-in drivers (postgres, sqlserver, oracle, sqlite) are registered at
import time. Custom drivers register via:

    from src.engine import register_driver, Driver

    class MyDriver(Driver):
        ...

    register_driver("mydb", MyDriver)
"""

from src.core.databases.connections.database import Database as Driver
from src.core.databases.connections.postgres_connection import PostgresDB
from src.core.databases.connections.sqlserver_connection import SqlserverDB
from src.core.databases.connections.oracle_connection import OracleDB
from src.core.databases.connections.sqlite_connection import SqliteDB

_DRIVERS: dict = {
    "pgsql": PostgresDB,
    "postgres": PostgresDB,
    "sqlserver": SqlserverDB,
    "oracle": OracleDB,
    "sqlite": SqliteDB,
}


class DriverNotFoundError(ValueError):
    pass


def register_driver(name: str, cls: type) -> None:
    """Register a driver class under `name`. Idempotent for same class; raises
    if a different class is already registered under the name."""
    existing = _DRIVERS.get(name)
    if existing is not None and existing is not cls:
        raise ValueError(
            f"driver '{name}' already registered as {existing.__name__}; "
            f"refusing to overwrite with {cls.__name__}"
        )
    _DRIVERS[name] = cls


def get_driver(name: str) -> Driver:
    """Resolve a driver by name and return a fresh instance."""
    cls = _DRIVERS.get(name)
    if cls is None:
        raise DriverNotFoundError(
            f"driver '{name}' not found. registered: {sorted(_DRIVERS)}"
        )
    return cls()


def list_drivers() -> list:
    return sorted(_DRIVERS)


__all__ = [
    "Driver",
    "register_driver",
    "get_driver",
    "list_drivers",
    "DriverNotFoundError",
]
