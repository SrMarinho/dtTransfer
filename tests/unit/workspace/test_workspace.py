import pytest
from pathlib import Path
from pydantic import ValidationError

from src.engine.workspace.workspace import Workspace, WorkspaceKind, ConnectionRef


class TestWorkspaceModel:
    def test_minimal_yaml_workspace(self, tmp_path):
        ws = Workspace(
            id="acme",
            kind=WorkspaceKind.YAML,
            root_path=tmp_path,
            target=ConnectionRef(driver="postgres", env_prefix="DB_ACME_POSTGRES"),
        )
        assert ws.id == "acme"
        assert ws.kind == WorkspaceKind.YAML
        assert ws.sources == []
        assert ws.entities_dir == tmp_path / "entities"
        assert ws.sql_dir == tmp_path / "sqls"
        assert ws.migrations_dir == tmp_path / "migrations"

    def test_python_workspace_legacy(self, tmp_path):
        ws = Workspace(
            id="biSenior",
            kind=WorkspaceKind.PYTHON,
            root_path=tmp_path,
            target=ConnectionRef(driver="postgres", env_prefix="DB_BISENIOR_POSTGRES"),
        )
        assert ws.kind == WorkspaceKind.PYTHON

    def test_id_must_be_slug(self):
        with pytest.raises(ValidationError):
            Workspace(
                id="bad id with spaces",
                kind=WorkspaceKind.YAML,
                root_path=Path("/tmp/x"),
                target=ConnectionRef(driver="postgres", env_prefix="DB_X"),
            )

    def test_id_rejects_empty(self):
        with pytest.raises(ValidationError):
            Workspace(
                id="",
                kind=WorkspaceKind.YAML,
                root_path=Path("/tmp/x"),
                target=ConnectionRef(driver="postgres", env_prefix="DB_X"),
            )

    def test_kind_rejects_invalid(self, tmp_path):
        with pytest.raises(ValidationError):
            Workspace(
                id="x",
                kind="banana",
                root_path=tmp_path,
                target=ConnectionRef(driver="postgres", env_prefix="DB_X"),
            )

    def test_sources_multiple(self, tmp_path):
        ws = Workspace(
            id="x",
            kind=WorkspaceKind.YAML,
            root_path=tmp_path,
            target=ConnectionRef(driver="postgres", env_prefix="DB_X"),
            sources=[
                ConnectionRef(name="oracle_main", driver="oracle", env_prefix="DB_ORACLE"),
                ConnectionRef(name="ss", driver="sqlserver", env_prefix="DB_SS"),
            ],
        )
        assert len(ws.sources) == 2
        assert ws.sources[0].name == "oracle_main"


class TestConnectionRef:
    def test_driver_must_be_known(self):
        with pytest.raises(ValidationError):
            ConnectionRef(driver="mongodb", env_prefix="DB_X")

    def test_env_prefix_required(self):
        with pytest.raises(ValidationError):
            ConnectionRef(driver="postgres", env_prefix="")
