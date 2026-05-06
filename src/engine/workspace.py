"""Workspace API.

Re-exports the workspace public surface from the implementation modules.
"""

from src.engine.workspace.workspace import Workspace, WorkspaceKind, ConnectionRef
from src.engine.workspace.yaml_entity import EntitySpec, YamlTable, load_entities
from src.engine.workspace.registry import (
    WorkspaceRegistry,
    WorkspaceNotFoundError,
    DuplicateWorkspaceError,
)
from src.engine.workspace.loader import WorkspaceLoader

__all__ = [
    "Workspace",
    "WorkspaceKind",
    "ConnectionRef",
    "EntitySpec",
    "YamlTable",
    "load_entities",
    "WorkspaceRegistry",
    "WorkspaceNotFoundError",
    "DuplicateWorkspaceError",
    "WorkspaceLoader",
]
