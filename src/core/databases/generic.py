from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

from src.core.databases.fake_database import FakeDatabaseDriver
from src.core.logger.logging import logger
from src.engine.driver import get_driver
from src.engine.workspace.workspace import ConnectionRef


load_dotenv()


_DRIVER_KIND_MAP = {
    "postgres": "pgsql",
    "sqlserver": "sqlserver",
    "oracle": "oracle",
}


class GenericDatabase:
    """Driver-agnostic Database resolved from a ConnectionRef.

    Reads credentials from env vars under the ref's env_prefix.
    Layout: <PREFIX>_HOST, <PREFIX>_PORT, <PREFIX>_DATABASE,
    <PREFIX>_USERNAME, <PREFIX>_PASSWORD. Oracle also reads
    <PREFIX>_SERVICE_NAME and <PREFIX>_ENCODING.
    """

    def __init__(self, ref: ConnectionRef, workspace_id: str):
        self.ref = ref
        self.workspace_id = workspace_id
        self.name = f"{workspace_id}/{ref.name or ref.env_prefix}"
        p = ref.env_prefix
        self.driver = _DRIVER_KIND_MAP.get(ref.driver, ref.driver)
        self.host: Optional[str] = os.getenv(f"{p}_HOST")
        self.port: Optional[str] = os.getenv(f"{p}_PORT")
        self.database: Optional[str] = os.getenv(f"{p}_DATABASE") or os.getenv(f"{p}_SERVICE_NAME")
        self.username: Optional[str] = os.getenv(f"{p}_USERNAME") or os.getenv(f"{p}_USER")
        self.password: Optional[str] = os.getenv(f"{p}_PASSWORD")
        self.encoding: Optional[str] = os.getenv(f"{p}_ENCODING")

    def getDriver(self):
        return get_driver(self.driver)

    def connection(self):
        if self.ref.driver == "fake":
            fake = FakeDatabaseDriver(self.database, self.host, self.username, self.password)
            return fake.connection()
        try:
            return self.getDriver().connection(
                self.database, self.username, self.password, self.host, self.port
            )
        except Exception as e:
            logger.error(
                f"Erro ao conectar driver {self.driver} ws={self.workspace_id} ref={self.ref.name}: {e}"
            )
            raise


__all__ = ["GenericDatabase"]
