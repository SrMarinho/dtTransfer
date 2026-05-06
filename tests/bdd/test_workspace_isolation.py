from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.factories.entity_registry import EntityRegistry
from src.engine.workspace.bootstrap import bootstrap
from src.engine.workspace.loader import WorkspaceLoader
from src.engine.workspace.registry import WorkspaceRegistry
from src.engine.workspace.workspace import ConnectionRef, Workspace, WorkspaceKind


scenarios("features/workspace_isolation.feature")


REPO_BUILTIN = Path(__file__).resolve().parents[2] / "src" / "workspaces"


@pytest.fixture
def state(tmp_path, monkeypatch):
    reg = WorkspaceRegistry()
    reg.clear()
    EntityRegistry._workspace_entities = {}
    monkeypatch.delenv("WORKSPACES_DIR", raising=False)
    yield {"tmp": tmp_path, "monkeypatch": monkeypatch, "workspaces": {}}
    reg.clear()
    EntityRegistry._workspace_entities = {}


def _build_yaml(tmp_root: Path, ws_id: str, entity: str) -> Workspace:
    root = tmp_root / ws_id
    (root / "entities").mkdir(parents=True)
    (root / "sqls").mkdir(parents=True)
    (root / "entities" / f"{entity}.yml").write_text(
        f"name: {entity}\ntarget_table: {entity}\n"
        f"source: src\ntarget: tgt\n"
        f"process_type: full\nsql_file: {entity}.sql\n"
        f"columns:\n  - id\n",
        encoding="utf-8",
    )
    (root / "sqls" / f"{entity}.sql").write_text("SELECT 1", encoding="utf-8")
    return Workspace(
        id=ws_id,
        kind=WorkspaceKind.YAML,
        root_path=root,
        target=ConnectionRef(name="tgt", driver="postgres", env_prefix=f"DB_{ws_id.upper()}_T"),
        sources=[ConnectionRef(name="src", driver="postgres", env_prefix=f"DB_{ws_id.upper()}_S")],
    )


def _write_yaml_workspace_dir(root: Path, ws_id: str) -> None:
    d = root / ws_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "workspace.yml").write_text(
        f"id: {ws_id}\nkind: yaml\n"
        f"target:\n  driver: postgres\n  env_prefix: DB_{ws_id.upper()}_PG\n",
        encoding="utf-8",
    )
    (d / "entities").mkdir(exist_ok=True)
    (d / "sqls").mkdir(exist_ok=True)


@given("a clean registry")
def _clean(state):
    pass


@given(parsers.parse('a YAML workspace "{ws_id}" with entity "{entity}"'))
def _yaml_with(state, ws_id, entity):
    ws = _build_yaml(state["tmp"], ws_id, entity)
    state["workspaces"][ws_id] = ws
    WorkspaceRegistry().register(ws)


@given("built-in workspaces are loaded")
def _builtin(state):
    bootstrap(builtin_dir=REPO_BUILTIN)


@given(parsers.parse('an external workspace dir with "{ws_id}"'))
def _ext(state, ws_id):
    ext = state["tmp"] / "external"
    ext.mkdir(exist_ok=True)
    _write_yaml_workspace_dir(ext, ws_id)
    state["external_dir"] = ext
    state["monkeypatch"].setenv("WORKSPACES_DIR", str(ext))


@when("both workspaces register their entities")
def _register(state):
    for ws in state["workspaces"].values():
        EntityRegistry.register_yaml_workspace(ws)


@when("the loader runs with both dirs")
def _loader_both(state):
    loader = WorkspaceLoader(builtin_dir=REPO_BUILTIN, external_dir=state["external_dir"])
    loader.discover()


@then(parsers.parse('table "{key}" exists in EntityRegistry'))
def _table_exists(key):
    assert key in EntityRegistry.valid_tables()


@then(parsers.parse('table "{key}" does not exist'))
def _table_absent(key):
    assert key not in EntityRegistry.valid_tables()


@then(parsers.parse('the registry contains "{ws_id}"'))
def _reg_has(ws_id):
    assert ws_id in WorkspaceRegistry()

