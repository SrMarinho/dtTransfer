import pytest
from pathlib import Path

from src.engine.workspace.workspace import Workspace, WorkspaceKind, ConnectionRef
from src.engine.workspace.yaml_entity import (
    EntitySpec,
    EntityLoadError,
    YamlTable,
    load_entities,
)


@pytest.fixture
def ws_root(tmp_path):
    (tmp_path / "entities").mkdir()
    (tmp_path / "sqls").mkdir()
    return tmp_path


@pytest.fixture
def ws(ws_root):
    return Workspace(
        id="acme",
        kind=WorkspaceKind.YAML,
        root_path=ws_root,
        target=ConnectionRef(name="pg", driver="postgres", env_prefix="DB_ACME_PG"),
        sources=[ConnectionRef(name="src_pg", driver="postgres", env_prefix="DB_SRC_PG")],
    )


def _write_entity(ws_root: Path, name: str, body: str) -> Path:
    p = ws_root / "entities" / f"{name}.yml"
    p.write_text(body, encoding="utf-8")
    return p


class TestEntitySpec:
    def test_parse_minimal(self, ws_root):
        _write_entity(
            ws_root,
            "sample",
            "name: sample\n"
            "target_table: sample\n"
            "source: src_pg\n"
            "target: pg\n"
            "process_type: full\n"
            "sql_file: sample.sql\n"
            "columns:\n"
            "  - id\n"
            "  - nome\n",
        )
        specs = load_entities(ws_root / "entities")
        assert len(specs) == 1
        s = specs[0]
        assert s.name == "sample"
        assert s.target_table == "sample"
        assert s.source == "src_pg"
        assert s.process_type == "full"
        assert s.columns == ["id", "nome"]

    def test_invalid_process_type(self, ws_root):
        _write_entity(
            ws_root,
            "bad",
            "name: bad\ntarget_table: bad\nsource: a\ntarget: b\n"
            "process_type: weird\nsql_file: bad.sql\ncolumns: [id]\n",
        )
        with pytest.raises(EntityLoadError):
            load_entities(ws_root / "entities")

class TestYamlTable:
    def test_table_props_from_spec(self, ws):
        spec = EntitySpec(
            name="sample",
            target_table="sample",
            source="src_pg",
            target="pg",
            process_type="full",
            sql_file="sample.sql",
            columns=["id", "nome"],
        )
        (ws.sql_dir / "sample.sql").write_text("SELECT 1", encoding="utf-8")
        t = YamlTable(spec=spec, workspace=ws, params=None)
        assert t.name == "sample"
        assert t.columns == ["id", "nome"]
        assert t.fromDB == ("acme", "src_pg")
        assert t.toDB == ("acme", "pg")
        assert Path(t.query_path).name == "sample.sql"

    def test_get_query_reads_sql_file(self, ws):
        (ws.sql_dir / "q.sql").write_text("SELECT * FROM x", encoding="utf-8")
        spec = EntitySpec(
            name="x",
            target_table="x",
            source="src_pg",
            target="pg",
            process_type="full",
            sql_file="q.sql",
            columns=["id"],
        )
        t = YamlTable(spec=spec, workspace=ws, params=None)
        assert t.getQuery() == "SELECT * FROM x"
