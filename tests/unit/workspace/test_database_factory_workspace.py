import pytest

from src.factories.database_factory import Database, DatabaseFactory
from src.engine.workspace.registry import WorkspaceRegistry
from src.engine.workspace.workspace import ConnectionRef, Workspace, WorkspaceKind


@pytest.fixture
def fresh_registry():
    reg = WorkspaceRegistry()
    reg.clear()
    yield reg
    reg.clear()


@pytest.fixture
def env_postgres(monkeypatch):
    monkeypatch.setenv("DB_ACME_PG_HOST", "h.example")
    monkeypatch.setenv("DB_ACME_PG_PORT", "5432")
    monkeypatch.setenv("DB_ACME_PG_DATABASE", "acme")
    monkeypatch.setenv("DB_ACME_PG_USERNAME", "u")
    monkeypatch.setenv("DB_ACME_PG_PASSWORD", "p")


def _make_ws(tmp_path, sources=None):
    return Workspace(
        id="acme",
        kind=WorkspaceKind.YAML,
        root_path=tmp_path,
        target=ConnectionRef(name="pg", driver="postgres", env_prefix="DB_ACME_PG"),
        sources=sources or [
            ConnectionRef(name="src_pg", driver="postgres", env_prefix="DB_ACME_PG"),
        ],
    )


class TestLegacyEnumStillWorks:
    def test_fake_database_via_enum(self):
        inst = DatabaseFactory.getInstance(Database.FAKEDATABASE)
        assert inst.name == "FakeDatabase"


class TestWorkspaceTuple:
    def test_resolve_target_postgres(self, tmp_path, fresh_registry, env_postgres):
        ws = _make_ws(tmp_path)
        fresh_registry.register(ws)
        inst = DatabaseFactory.getInstance(("acme", "pg"))
        assert inst.host == "h.example"
        assert inst.database == "acme"

    def test_resolve_source_by_name(self, tmp_path, fresh_registry, env_postgres):
        ws = _make_ws(tmp_path)
        fresh_registry.register(ws)
        inst = DatabaseFactory.getInstance(("acme", "src_pg"))
        assert inst.host == "h.example"

    def test_unknown_workspace_raises(self, fresh_registry):
        with pytest.raises(ValueError):
            DatabaseFactory.getInstance(("nope", "pg"))

    def test_unknown_ref_raises(self, tmp_path, fresh_registry, env_postgres):
        fresh_registry.register(_make_ws(tmp_path))
        with pytest.raises(ValueError):
            DatabaseFactory.getInstance(("acme", "ghost"))

    def test_fake_driver_via_workspace(self, tmp_path, fresh_registry):
        ws = Workspace(
            id="t",
            kind=WorkspaceKind.YAML,
            root_path=tmp_path,
            target=ConnectionRef(name="fk", driver="fake", env_prefix="UNUSED"),
        )
        fresh_registry.register(ws)
        inst = DatabaseFactory.getInstance(("t", "fk"))
        assert inst.ref.driver == "fake"
        conn = inst.connection()
        assert conn is not None
