from pathlib import Path

import pytest

from src.factories.entity_registry import EntityRegistry
from src.engine.workspace.bootstrap import bootstrap
from src.engine.workspace.loader import WorkspaceLoader
from src.engine.workspace.registry import WorkspaceRegistry


@pytest.fixture
def fresh():
    reg = WorkspaceRegistry()
    reg.clear()
    yield reg
    reg.clear()


REPO_BUILTIN = Path(__file__).resolve().parents[3] / "src" / "workspaces"


class TestLegacyAdapters:
    def test_discover_legacy_workspaces(self, fresh):
        loader = WorkspaceLoader(builtin_dir=REPO_BUILTIN)
        loader.discover()
        ids = [w.id for w in fresh.list()]
        assert "biSenior" in ids
        assert "biMktNaz" in ids
        assert "biNazaria" in ids

    def test_legacy_entities_still_registered(self, fresh):
        bootstrap()
        tables = EntityRegistry.valid_tables()
        assert "biSenior/titulos_receber" in tables
        assert "biMktNaz/ac_recebimentos" in tables
        assert "biNazaria/curva" in tables

