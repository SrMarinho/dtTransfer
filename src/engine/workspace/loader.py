from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import List, Optional

import yaml

from src.engine.workspace.workspace import ConnectionRef, Workspace, WorkspaceKind
from src.engine.workspace.registry import (
    DuplicateWorkspaceError,
    WorkspaceRegistry,
)


class WorkspaceLoadError(Exception):
    pass


class WorkspaceLoader:
    """Discovers workspaces from built-in and external dirs.

    Built-in dir takes precedence on id conflict.
    External dir comes from env var WORKSPACES_DIR (or constructor param).
    """

    def __init__(
        self,
        builtin_dir: Optional[Path] = None,
        external_dir: Optional[Path] = None,
    ):
        self.builtin_dir = Path(builtin_dir) if builtin_dir else None
        if external_dir is not None:
            self.external_dir = Path(external_dir)
        else:
            env = os.getenv("WORKSPACES_DIR")
            self.external_dir = Path(env) if env else None

    def discover(self) -> List[Workspace]:
        registry = WorkspaceRegistry()
        seen: set = set()
        loaded: List[Workspace] = []

        # built-in first → precedence
        for d in self._iter_dirs(self.builtin_dir):
            ws = self._try_load(d)
            if ws is not None and ws.id not in seen:
                seen.add(ws.id)
                if ws.id not in registry:
                    registry.register(ws)
                loaded.append(ws)

        for d in self._iter_dirs(self.external_dir):
            ws = self._try_load(d)
            if ws is None:
                continue
            if ws.id in seen:
                continue  # built-in wins
            seen.add(ws.id)
            try:
                registry.register(ws)
            except DuplicateWorkspaceError:
                continue
            loaded.append(ws)

        return loaded

    def _iter_dirs(self, base: Optional[Path]):
        if base is None or not base.exists() or not base.is_dir():
            return
        for child in sorted(base.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                yield child

    def _try_load(self, path: Path) -> Optional[Workspace]:
        yml = path / "workspace.yml"
        py = path / "__init__.py"
        if yml.exists():
            ws = self._load_yaml(path, yml)
        elif py.exists():
            ws = self._load_python(path, py)
        else:
            return None
        if ws is not None and not ws.enabled:
            return None
        return ws

    def _load_yaml(self, root: Path, yml: Path) -> Optional[Workspace]:
        try:
            data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            return None
        if not isinstance(data, dict):
            return None
        try:
            target = ConnectionRef(**data["target"]) if "target" in data else None
            sources = [ConnectionRef(**s) for s in data.get("sources", [])]
            return Workspace(
                id=data.get("id", root.name),
                kind=WorkspaceKind(data.get("kind", "yaml")),
                enabled=data.get("enabled", True),
                root_path=root,
                target=target,
                sources=sources,
            )
        except Exception:
            return None

    def _load_python(self, root: Path, py: Path) -> Optional[Workspace]:
        mod_name = f"_ws_{root.name}_{abs(hash(str(root)))}"
        spec = importlib.util.spec_from_file_location(mod_name, py)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            return None
        builder = getattr(module, "build", None)
        if not callable(builder):
            return None
        try:
            ws = builder(root)
        except Exception:
            return None
        return ws if isinstance(ws, Workspace) else None


__all__ = ["WorkspaceLoader", "WorkspaceLoadError"]
