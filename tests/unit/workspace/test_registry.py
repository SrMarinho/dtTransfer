import pytest

from src.engine.workspace.workspace import Workspace, WorkspaceKind, ConnectionRef
from src.engine.workspace.registry import WorkspaceRegistry, DuplicateWorkspaceError, WorkspaceNotFoundError


@pytest.fixture
def fresh_registry():
    reg = WorkspaceRegistry()
    reg.clear()
    yield reg
    reg.clear()


def _ws(id_: str, tmp_path, kind=WorkspaceKind.YAML) -> Workspace:
    root = tmp_path / id_
    root.mkdir(exist_ok=True)
    return Workspace(
        id=id_,
        kind=kind,
        root_path=root,
        target=ConnectionRef(driver="postgres", env_prefix=f"DB_{id_.upper()}"),
    )


class TestWorkspaceRegistry:
    def test_register_and_get(self, fresh_registry, tmp_path):
        ws = _ws("alpha", tmp_path)
        fresh_registry.register(ws)
        assert fresh_registry.get("alpha") is ws

    def test_get_missing_raises(self, fresh_registry):
        with pytest.raises(WorkspaceNotFoundError):
            fresh_registry.get("nope")

    def test_duplicate_id_raises(self, fresh_registry, tmp_path):
        fresh_registry.register(_ws("dup", tmp_path))
        with pytest.raises(DuplicateWorkspaceError):
            fresh_registry.register(_ws("dup", tmp_path))

    def test_list_returns_sorted(self, fresh_registry, tmp_path):
        fresh_registry.register(_ws("zeta", tmp_path))
        fresh_registry.register(_ws("alpha", tmp_path))
        fresh_registry.register(_ws("mu", tmp_path))
        assert [w.id for w in fresh_registry.list()] == ["alpha", "mu", "zeta"]

    def test_clear(self, fresh_registry, tmp_path):
        fresh_registry.register(_ws("a", tmp_path))
        fresh_registry.clear()
        assert fresh_registry.list() == []

    def test_singleton_shared(self, fresh_registry, tmp_path):
        fresh_registry.register(_ws("x", tmp_path))
        other = WorkspaceRegistry()
        assert other.get("x").id == "x"

    def test_default_when_single(self, fresh_registry, tmp_path):
        fresh_registry.register(_ws("solo", tmp_path))
        assert fresh_registry.default().id == "solo"

    def test_default_raises_when_multiple(self, fresh_registry, tmp_path):
        fresh_registry.register(_ws("a", tmp_path))
        fresh_registry.register(_ws("b", tmp_path))
        with pytest.raises(WorkspaceNotFoundError):
            fresh_registry.default()

    def test_default_raises_when_empty(self, fresh_registry):
        with pytest.raises(WorkspaceNotFoundError):
            fresh_registry.default()
