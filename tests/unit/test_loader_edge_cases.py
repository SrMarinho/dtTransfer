"""WorkspaceLoader edge cases: broken YAML, missing files, empty dirs."""
from pathlib import Path
import pytest
from src.engine.workspace.loader import WorkspaceLoader
from src.engine.workspace.registry import WorkspaceRegistry


@pytest.fixture
def fresh():
    reg = WorkspaceRegistry()
    reg.clear()
    yield
    reg.clear()


def test_empty_builtin_dir_returns_empty(fresh, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    loader = WorkspaceLoader(builtin_dir=empty)
    result = loader.discover()
    assert result == []


def test_builtin_dir_does_not_exist_returns_empty(fresh, tmp_path):
    loader = WorkspaceLoader(builtin_dir=tmp_path / "nonexistent")
    result = loader.discover()
    assert result == []


def test_builtin_dir_is_none_returns_empty(fresh):
    loader = WorkspaceLoader(builtin_dir=None)
    result = loader.discover()
    assert result == []


def test_dir_with_workspace_yml_loads(fresh, tmp_path):
    ws_dir = tmp_path / "myws"
    ws_dir.mkdir()
    (ws_dir / "workspace.yml").write_text(
        "id: myws\nkind: yaml\ntarget:\n  driver: sqlite\n  env_prefix: DB_MYWS\n",
        encoding="utf-8",
    )
    (ws_dir / "entities").mkdir()
    (ws_dir / "sqls").mkdir()
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    ids = [w.id for w in result]
    assert "myws" in ids


def test_dir_without_workspace_yml_or_init_is_ignored(fresh, tmp_path):
    ws_dir = tmp_path / "broken"
    ws_dir.mkdir()
    (ws_dir / "readme.txt").write_text("not a workspace")
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    assert all(w.id != "broken" for w in result)


def test_broken_yaml_returns_none(fresh, tmp_path):
    ws_dir = tmp_path / "badyml"
    ws_dir.mkdir()
    (ws_dir / "workspace.yml").write_text("{bad: yaml: unclosed", encoding="utf-8")
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    assert all(w.id != "badyml" for w in result)


def test_yaml_without_target_is_not_loaded(fresh, tmp_path):
    ws_dir = tmp_path / "notarget"
    ws_dir.mkdir()
    (ws_dir / "workspace.yml").write_text(
        "id: notarget\nkind: yaml\nsources: []\n", encoding="utf-8"
    )
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    ids = [w.id for w in result]
    assert "notarget" not in ids


def test_yaml_with_missing_source_driver(fresh, tmp_path):
    ws_dir = tmp_path / "badsrc"
    ws_dir.mkdir()
    (ws_dir / "workspace.yml").write_text(
        "id: badsrc\nkind: yaml\ntarget:\n  driver: sqlite\n  env_prefix: DB_X\nsources:\n  - name: src\n",
        encoding="utf-8",
    )
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    # source with missing driver → ConnectionRef validation fails → workspace not loaded
    assert all(w.id != "badsrc" for w in result)


def test_python_workspace_missing_build_fn(fresh, tmp_path):
    ws_dir = tmp_path / "nobuild"
    ws_dir.mkdir()
    (ws_dir / "__init__.py").write_text("x = 1\n", encoding="utf-8")
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    assert all(w.id != "nobuild" for w in result)


def test_python_workspace_module_error(fresh, tmp_path):
    ws_dir = tmp_path / "broke"
    ws_dir.mkdir()
    (ws_dir / "__init__.py").write_text("import nonexistent_module\n", encoding="utf-8")
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    assert all(w.id != "broke" for w in result)


def test_discover_is_idempotent(fresh, tmp_path):
    ws_dir = tmp_path / "dup"
    ws_dir.mkdir()
    (ws_dir / "workspace.yml").write_text(
        "id: dup\nkind: yaml\ntarget:\n  driver: sqlite\n  env_prefix: DB_DUP\n",
        encoding="utf-8",
    )
    (ws_dir / "entities").mkdir()
    (ws_dir / "sqls").mkdir()
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    first = loader.discover()
    second = loader.discover()
    assert len(first) == len(second)


def test_directory_starts_with_dot_is_ignored(fresh, tmp_path):
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    (hidden / "workspace.yml").write_text(
        "id: hidden\nkind: yaml\ntarget:\n  driver: sqlite\n  env_prefix: DB_H\n",
        encoding="utf-8",
    )
    loader = WorkspaceLoader(builtin_dir=tmp_path)
    result = loader.discover()
    assert all(w.id != "hidden" for w in result)
