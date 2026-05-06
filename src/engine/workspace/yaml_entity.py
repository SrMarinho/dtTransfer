from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.entity import Entity
from src.engine.workspace.workspace import Workspace


_PROCESS_TYPES = {"full", "incremental", "monthly", "unit"}


class EntityLoadError(Exception):
    pass


class EntitySpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    target_table: str
    source: str
    target: str
    process_type: str
    sql_file: str
    incremental_column: Optional[str] = None
    columns: List[str] = Field(default_factory=list)

    @field_validator("process_type")
    @classmethod
    def _proc(cls, v: str) -> str:
        if v not in _PROCESS_TYPES:
            raise ValueError(f"process_type must be one of {sorted(_PROCESS_TYPES)}")
        return v


def load_entities(entities_dir: Path) -> List[EntitySpec]:
    if not entities_dir.exists():
        return []
    specs: List[EntitySpec] = []
    for yml in sorted(entities_dir.glob("*.yml")):
        try:
            data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
            data.pop("$schema", None)
            specs.append(EntitySpec(**data))
        except Exception as e:
            raise EntityLoadError(f"failed to load {yml.name}: {e}") from e
    return specs


class YamlTable(Entity):
    """Entity subclass driven by EntitySpec from a YAML workspace.

    fromDB/toDB are tuples (workspace_id, connection_ref) — resolved by the
    workspace-aware DatabaseFactory at runtime, not by the legacy Database enum.
    """

    def __init__(self, spec: EntitySpec, workspace: Workspace, params: Any = None):
        super().__init__(params)
        self.spec = spec
        self.workspace = workspace
        self.name = spec.target_table
        self.columns = list(spec.columns)
        self.fromDB = (workspace.id, spec.source)
        self.toDB = (workspace.id, spec.target)
        self.query_path = str(workspace.sql_dir / spec.sql_file)
        self.incremental_column = spec.incremental_column

    def get_system_sql_path(self) -> Path:
        return Path(self.query_path)

    def createTable(self):
        from src.engine.workspace.migrations import run_alembic
        run_alembic(self.workspace, "upgrade", "head")


__all__ = ["EntitySpec", "YamlTable", "load_entities", "EntityLoadError"]
