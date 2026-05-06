from pathlib import Path

import pytest

from src.factories.entity_registry import EntityRegistry
from src.engine.workspace.bootstrap import DEFAULT_BUILTIN, bootstrap
from src.engine.workspace.migrations import current_head, run_alembic
from src.engine.workspace.registry import WorkspaceRegistry
from src.engine.workspace.yaml_entity import YamlTable


@pytest.fixture
def fresh():
    reg = WorkspaceRegistry()
    reg.clear()
    EntityRegistry._workspace_entities = {}
    yield reg
    reg.clear()
    EntityRegistry._workspace_entities = {}


class TestExampleWorkspace:
    def test_discovered_as_yaml(self, fresh):
        bootstrap()
        ws = fresh.get("example")
        assert ws.kind.value == "yaml"
        assert ws.target.name == "target_pg"

    def test_entity_registers_under_workspace_namespace(self, fresh):
        bootstrap()
        ws = fresh.get("example")
        EntityRegistry.register_yaml_workspace(ws)
        assert "example/sample" in EntityRegistry.valid_tables()
        inst = EntityRegistry.getInstance("example/sample", {"table": "example/sample"})
        assert isinstance(inst, YamlTable)
        assert inst.columns == ["id", "nome", "criado_em"]

    def test_migration_runs_against_sqlite(self, fresh, tmp_path, monkeypatch):
        monkeypatch.setenv("DB_EXAMPLE_SQLITE_DATABASE", str(tmp_path / "ex.db"))
        bootstrap()
        ws = fresh.get("example")
        run_alembic(ws, "upgrade", "head")
        assert current_head(ws) == "0001"

