from __future__ import annotations

import re
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


_SLUG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_\-]*$")
_KNOWN_DRIVERS = {"postgres", "sqlserver", "oracle", "sqlite", "fake"}


class WorkspaceKind(str, Enum):
    YAML = "yaml"
    PYTHON = "python"


class ConnectionRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    driver: str
    env_prefix: str = Field(min_length=1)
    options: dict = Field(default_factory=dict)

    @field_validator("driver")
    @classmethod
    def _driver_known(cls, v: str) -> str:
        if v not in _KNOWN_DRIVERS:
            raise ValueError(f"unknown driver '{v}'. allowed: {sorted(_KNOWN_DRIVERS)}")
        return v


class Workspace(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    id: str
    kind: WorkspaceKind
    root_path: Path
    enabled: bool = True
    target: ConnectionRef
    sources: List[ConnectionRef] = Field(default_factory=list)
    entities_dir: Optional[Path] = None
    sql_dir: Optional[Path] = None
    migrations_dir: Optional[Path] = None

    @field_validator("id")
    @classmethod
    def _id_slug(cls, v: str) -> str:
        if not _SLUG_RE.match(v):
            raise ValueError(
                "id must start with a letter and contain only letters, digits, '_' or '-'"
            )
        return v

    @model_validator(mode="after")
    def _default_paths(self) -> "Workspace":
        if self.entities_dir is None:
            object.__setattr__(self, "entities_dir", self.root_path / "entities")
        if self.sql_dir is None:
            object.__setattr__(self, "sql_dir", self.root_path / "sqls")
        if self.migrations_dir is None:
            object.__setattr__(self, "migrations_dir", self.root_path / "migrations")
        return self


__all__ = ["Workspace", "WorkspaceKind", "ConnectionRef"]
