from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from src.engine.workspace.workspace import ConnectionRef, Workspace


class HeadOutOfSyncError(Exception):
    pass


_REV_RE = re.compile(r'^revision\s*=\s*[\'"]([^\'"]+)[\'"]', re.MULTILINE)


def build_sqlalchemy_url(ref: ConnectionRef) -> str:
    p = ref.env_prefix
    if ref.driver == "sqlite":
        db = os.getenv(f"{p}_DATABASE", "")
        # sqlite:////absolute/path or sqlite:///relative
        if db.startswith("/") or (len(db) > 1 and db[1] == ":"):
            return f"sqlite:////{db.lstrip('/')}" if db.startswith("/") else f"sqlite:///{db}"
        return f"sqlite:///{db}"
    if ref.driver == "postgres":
        return (
            f"postgresql+psycopg2://{os.getenv(f'{p}_USERNAME')}:"
            f"{os.getenv(f'{p}_PASSWORD')}@{os.getenv(f'{p}_HOST')}:"
            f"{os.getenv(f'{p}_PORT', '5432')}/{os.getenv(f'{p}_DATABASE')}"
        )
    if ref.driver == "sqlserver":
        return (
            f"mssql+pyodbc://{os.getenv(f'{p}_USERNAME')}:"
            f"{os.getenv(f'{p}_PASSWORD')}@{os.getenv(f'{p}_HOST')}:"
            f"{os.getenv(f'{p}_PORT', '1433')}/{os.getenv(f'{p}_DATABASE')}"
        )
    if ref.driver == "oracle":
        return (
            f"oracle+oracledb://{os.getenv(f'{p}_USER') or os.getenv(f'{p}_USERNAME')}:"
            f"{os.getenv(f'{p}_PASSWORD')}@{os.getenv(f'{p}_HOST')}:"
            f"{os.getenv(f'{p}_PORT', '1521')}/?service_name="
            f"{os.getenv(f'{p}_SERVICE_NAME') or os.getenv(f'{p}_DATABASE')}"
        )
    raise ValueError(f"unsupported driver for sqlalchemy url: {ref.driver}")


def _alembic_config(ws: Workspace) -> Config:
    cfg = Config()
    cfg.set_main_option("script_location", str(ws.migrations_dir))
    cfg.set_main_option("sqlalchemy.url", build_sqlalchemy_url(ws.target))
    cfg.set_main_option("file_template", "%%(rev)s_%%(slug)s")
    return cfg


def run_alembic(ws: Workspace, action: str, *args: str, **kwargs) -> None:
    cfg = _alembic_config(ws)
    fn = getattr(command, action)
    fn(cfg, *args, **kwargs)


def available_head(ws: Workspace) -> Optional[str]:
    cfg = _alembic_config(ws)
    script = ScriptDirectory.from_config(cfg)
    return script.get_current_head()


def current_head(ws: Workspace) -> Optional[str]:
    cfg = _alembic_config(ws)
    from sqlalchemy import create_engine
    engine = create_engine(cfg.get_main_option("sqlalchemy.url"))
    from alembic.runtime.migration import MigrationContext
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        return ctx.get_current_revision()


def is_up_to_date(ws: Workspace) -> bool:
    return available_head(ws) == current_head(ws)


def validate_head(ws: Workspace) -> None:
    if not is_up_to_date(ws):
        raise HeadOutOfSyncError(
            f"workspace '{ws.id}' migrations out of sync: "
            f"db={current_head(ws)} expected={available_head(ws)}. "
            f"Run: python run.py migrate --workspace {ws.id} upgrade head"
        )


__all__ = [
    "build_sqlalchemy_url",
    "run_alembic",
    "current_head",
    "available_head",
    "is_up_to_date",
    "validate_head",
    "HeadOutOfSyncError",
]
