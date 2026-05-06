from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.engine.workspace.loader import WorkspaceLoader
from src.engine.workspace.registry import WorkspaceRegistry


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BUILTIN = REPO_ROOT / "src" / "workspaces"


def bootstrap(builtin_dir: Optional[Path] = None, external_dir: Optional[Path] = None) -> None:
    """Discovers and registers all workspaces. Idempotent: re-running is a no-op."""
    registry = WorkspaceRegistry()
    if registry.list():
        return
    loader = WorkspaceLoader(
        builtin_dir=builtin_dir or DEFAULT_BUILTIN,
        external_dir=external_dir,
    )
    loader.discover()

    # Register YAML workspace entities with EntityRegistry
    from src.factories.entity_registry import EntityRegistry
    for ws in registry.list():
        if ws.kind.value == "yaml":
            EntityRegistry.register_yaml_workspace(ws)


__all__ = ["bootstrap", "DEFAULT_BUILTIN"]
