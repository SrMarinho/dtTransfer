import pytest
from typer.testing import CliRunner

from src.interfaces.cli.commands.list_workspaces import app as list_workspaces_app
from src.engine.workspace.bootstrap import bootstrap
from src.engine.workspace.registry import WorkspaceRegistry


@pytest.fixture
def fresh():
    reg = WorkspaceRegistry()
    reg.clear()
    yield reg
    reg.clear()


def test_list_workspaces_shows_legacy_bundles(fresh):
    bootstrap()
    runner = CliRunner()
    result = runner.invoke(list_workspaces_app, [])
    assert result.exit_code == 0
    assert "biSenior" in result.stdout
    assert "biMktNaz" in result.stdout
    assert "biNazaria" in result.stdout


def test_list_workspaces_empty(fresh, monkeypatch, tmp_path):
    monkeypatch.setattr("src.engine.workspace.bootstrap.DEFAULT_BUILTIN", tmp_path / "empty")
    runner = CliRunner()
    result = runner.invoke(list_workspaces_app, [])
    assert result.exit_code == 0
    assert "Nenhum" in result.stdout
