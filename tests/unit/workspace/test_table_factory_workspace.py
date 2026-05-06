import pytest
from pathlib import Path

from src.factories.entity_registry import EntityRegistry
from src.engine.workspace.registry import WorkspaceRegistry
from src.engine.workspace.workspace import ConnectionRef, Workspace, WorkspaceKind


@pytest.fixture
def fresh_registry():
    reg = WorkspaceRegistry()
    reg.clear()
    EntityRegistry._workspace_entities = {}
    yield reg
    reg.clear()
    EntityRegistry._workspace_entities = {}


def _build_yaml_ws(tmp_path, ws_id: str, entities: list[tuple[str, list[str]]]) -> Workspace:
    root = tmp_path / ws_id
    (root / "entities").mkdir(parents=True)
    (root / "sqls").mkdir(parents=True)
    for ent_name, cols in entities:
        cols_yaml = "\n".join(f"  - {c}" for c in cols)
        (root / "entities" / f"{ent_name}.yml").write_text(
            f"name: {ent_name}\ntarget_table: {ent_name}\n"
            f"source: src\ntarget: tgt\n"
            f"process_type: full\nsql_file: {ent_name}.sql\n"
            f"columns:\n{cols_yaml}\n",
            encoding="utf-8",
        )
        (root / "sqls" / f"{ent_name}.sql").write_text("SELECT 1", encoding="utf-8")
    return Workspace(
        id=ws_id,
        kind=WorkspaceKind.YAML,
        root_path=root,
        target=ConnectionRef(name="tgt", driver="postgres", env_prefix=f"DB_{ws_id.upper()}_T"),
        sources=[ConnectionRef(name="src", driver="postgres", env_prefix=f"DB_{ws_id.upper()}_S")],
    )


class TestYamlWorkspaceRegistration:
    def test_register_yaml_workspace(self, tmp_path, fresh_registry):
        ws = _build_yaml_ws(tmp_path, "ws_a", [("foo", ["id", "x"])])
        fresh_registry.register(ws)
        EntityRegistry.register_yaml_workspace(ws)
        assert "ws_a/foo" in EntityRegistry.valid_tables()

    def test_get_instance_returns_yaml_table(self, tmp_path, fresh_registry):
        ws = _build_yaml_ws(tmp_path, "wsb", [("bar", ["id"])])
        fresh_registry.register(ws)
        EntityRegistry.register_yaml_workspace(ws)
        from src.engine.workspace.yaml_entity import YamlTable
        inst = EntityRegistry.getInstance("wsb/bar", {"table": "wsb/bar"})
        assert isinstance(inst, YamlTable)
        assert inst.name == "bar"

    def test_isolation_between_workspaces(self, tmp_path, fresh_registry):
        ws1 = _build_yaml_ws(tmp_path, "wsx", [("entx", ["id"])])
        ws2 = _build_yaml_ws(tmp_path, "wsy", [("enty", ["id"])])
        fresh_registry.register(ws1)
        fresh_registry.register(ws2)
        EntityRegistry.register_yaml_workspace(ws1)
        EntityRegistry.register_yaml_workspace(ws2)
        tables = EntityRegistry.valid_tables()
        assert "wsx/entx" in tables
        assert "wsy/enty" in tables
        # cross-leak: wsx must not contain enty
        listed_x = EntityRegistry.list_tables(system="wsx")
        assert "wsx/entx" in listed_x
        assert "wsy/enty" not in listed_x

    def test_unknown_entity_raises(self, fresh_registry):
        with pytest.raises(ValueError):
            EntityRegistry.getInstance("ghost/nope", {})

