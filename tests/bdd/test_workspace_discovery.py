from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.engine.workspace.registry import WorkspaceRegistry
from src.engine.workspace.loader import WorkspaceLoader


scenarios("features/workspace_discovery.feature")


@pytest.fixture
def state(tmp_path, monkeypatch):
    reg = WorkspaceRegistry()
    reg.clear()
    builtin = tmp_path / "builtin"
    builtin.mkdir()
    monkeypatch.delenv("WORKSPACES_DIR", raising=False)
    yield {"builtin": builtin, "external": None, "tmp": tmp_path, "monkeypatch": monkeypatch}
    reg.clear()


def _write_yaml_ws(root: Path, ws_id: str) -> None:
    d = root / ws_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "workspace.yml").write_text(
        f"id: {ws_id}\n"
        f"kind: yaml\n"
        f"target:\n"
        f"  driver: postgres\n"
        f"  env_prefix: DB_{ws_id.upper()}_PG\n",
        encoding="utf-8",
    )
    (d / "entities").mkdir(exist_ok=True)
    (d / "sqls").mkdir(exist_ok=True)


def _write_py_ws(root: Path, ws_id: str) -> None:
    d = root / ws_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "__init__.py").write_text(
        "from src.engine.workspace.workspace import Workspace, WorkspaceKind, ConnectionRef\n"
        "from pathlib import Path\n"
        "def build(root_path: Path) -> Workspace:\n"
        f"    return Workspace(id='{ws_id}', kind=WorkspaceKind.PYTHON, root_path=root_path,\n"
        f"        target=ConnectionRef(driver='postgres', env_prefix='DB_{ws_id.upper()}_PG'))\n"
        "def register(engine):\n"
        "    pass\n",
        encoding="utf-8",
    )


@given(parsers.parse('a built-in workspace dir "{builtin_label}"'))
def _builtin_dir(state, builtin_label):
    state["builtin_label"] = builtin_label


@given("an external workspace dir")
def _external_dir(state):
    ext = state["tmp"] / "external"
    ext.mkdir()
    state["external"] = ext
    state["monkeypatch"].setenv("WORKSPACES_DIR", str(ext))


@given(parsers.parse('a YAML workspace "{ws_id}" exists in built-in'))
def _yaml_in_builtin(state, ws_id):
    _write_yaml_ws(state["builtin"], ws_id)


@given(parsers.parse('a YAML workspace "{ws_id}" exists in external'))
def _yaml_in_external(state, ws_id):
    _write_yaml_ws(state["external"], ws_id)


@given(parsers.parse('a Python workspace "{ws_id}" exists in built-in'))
def _py_in_builtin(state, ws_id):
    _write_py_ws(state["builtin"], ws_id)


@given(parsers.parse('an invalid folder "{name}" exists in built-in'))
def _invalid_folder(state, name):
    d = state["builtin"] / name
    d.mkdir()
    (d / "garbage.txt").write_text("not a workspace", encoding="utf-8")


@when("the loader discovers workspaces")
def _discover(state):
    loader = WorkspaceLoader(builtin_dir=state["builtin"])
    loader.discover()


@then(parsers.parse('the registry contains "{ws_id}"'))
def _has(ws_id):
    assert ws_id in WorkspaceRegistry()


@then(parsers.parse('the registry does not contain "{ws_id}"'))
def _hasnot(ws_id):
    assert ws_id not in WorkspaceRegistry()


@then(parsers.parse('workspace "{ws_id}" has kind "{kind}"'))
def _kind(ws_id, kind):
    ws = WorkspaceRegistry().get(ws_id)
    assert ws.kind.value == kind


@then(parsers.parse('workspace "{ws_id}" comes from "{origin}"'))
def _origin(state, ws_id, origin):
    ws = WorkspaceRegistry().get(ws_id)
    if origin == "built-in":
        assert state["builtin"] in ws.root_path.parents or ws.root_path.is_relative_to(state["builtin"])
    else:
        assert ws.root_path.is_relative_to(state["external"])
