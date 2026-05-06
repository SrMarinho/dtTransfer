from __future__ import annotations

from threading import Lock
from typing import Dict, List

from src.engine.workspace.workspace import Workspace


class WorkspaceError(Exception):
    pass


class DuplicateWorkspaceError(WorkspaceError):
    pass


class WorkspaceNotFoundError(WorkspaceError):
    pass


class WorkspaceRegistry:
    _instance = None
    _instance_lock = Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._items: Dict[str, Workspace] = {}
                inst._lock = Lock()
                cls._instance = inst
            return cls._instance

    def register(self, ws: Workspace) -> None:
        with self._lock:
            if ws.id in self._items:
                raise DuplicateWorkspaceError(f"workspace '{ws.id}' already registered")
            self._items[ws.id] = ws

    def get(self, ws_id: str) -> Workspace:
        with self._lock:
            if ws_id not in self._items:
                raise WorkspaceNotFoundError(f"workspace '{ws_id}' not found")
            return self._items[ws_id]

    def list(self) -> List[Workspace]:
        with self._lock:
            return [self._items[k] for k in sorted(self._items)]

    def remove(self, ws_id: str) -> None:
        with self._lock:
            if ws_id not in self._items:
                raise WorkspaceNotFoundError(f"workspace '{ws_id}' not found")
            del self._items[ws_id]

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def default(self) -> Workspace:
        items = self.list()
        if len(items) == 0:
            raise WorkspaceNotFoundError("no workspaces registered")
        if len(items) > 1:
            raise WorkspaceNotFoundError(
                f"multiple workspaces registered ({[w.id for w in items]}); --workspace required"
            )
        return items[0]

    def __contains__(self, ws_id: str) -> bool:
        with self._lock:
            return ws_id in self._items


__all__ = [
    "WorkspaceRegistry",
    "WorkspaceError",
    "DuplicateWorkspaceError",
    "WorkspaceNotFoundError",
]
