import pytest

from src.engine.workspace.workspace import ConnectionRef, Workspace, WorkspaceKind
from src.engine.workspace.migrations import (
    build_sqlalchemy_url,
    run_alembic,
    current_head,
    available_head,
    is_up_to_date,
    HeadOutOfSyncError,
)


@pytest.fixture
def sqlite_ws(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_TEST_SQLITE_DATABASE", str(db_path))
    root = tmp_path / "ws"
    (root / "migrations" / "versions").mkdir(parents=True)
    (root / "migrations" / "env.py").write_text(_ENV_PY, encoding="utf-8")
    (root / "migrations" / "script.py.mako").write_text(_SCRIPT_MAKO, encoding="utf-8")
    return Workspace(
        id="test_ws",
        kind=WorkspaceKind.YAML,
        root_path=root,
        target=ConnectionRef(name="db", driver="sqlite", env_prefix="DB_TEST_SQLITE"),
    )


_ENV_PY = '''from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
'''

_SCRIPT_MAKO = """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
\"\"\"
from alembic import op
import sqlalchemy as sa

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
"""


_MIGRATION_001 = '''"""initial

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("widget", sa.Column("id", sa.Integer, primary_key=True))


def downgrade():
    op.drop_table("widget")
'''


def _write_initial(ws):
    p = ws.migrations_dir / "versions" / "0001_initial.py"
    p.write_text(_MIGRATION_001, encoding="utf-8")


class TestSqlalchemyUrlBuilder:
    def test_sqlite_url(self, monkeypatch):
        monkeypatch.setenv("DB_X_SQLITE_DATABASE", "/tmp/x.db")
        ref = ConnectionRef(driver="sqlite", env_prefix="DB_X_SQLITE")
        assert build_sqlalchemy_url(ref) == "sqlite:////tmp/x.db"

    def test_postgres_url(self, monkeypatch):
        monkeypatch.setenv("DB_PG_HOST", "h")
        monkeypatch.setenv("DB_PG_PORT", "5432")
        monkeypatch.setenv("DB_PG_DATABASE", "d")
        monkeypatch.setenv("DB_PG_USERNAME", "u")
        monkeypatch.setenv("DB_PG_PASSWORD", "p")
        ref = ConnectionRef(driver="postgres", env_prefix="DB_PG")
        assert build_sqlalchemy_url(ref) == "postgresql+psycopg2://u:p@h:5432/d"


class TestAlembicWorkspace:
    def test_upgrade_head_creates_version_table(self, sqlite_ws):
        _write_initial(sqlite_ws)
        run_alembic(sqlite_ws, "upgrade", "head")
        assert current_head(sqlite_ws) == "0001"

    def test_available_head_reads_versions_dir(self, sqlite_ws):
        _write_initial(sqlite_ws)
        assert available_head(sqlite_ws) == "0001"

    def test_is_up_to_date_after_upgrade(self, sqlite_ws):
        _write_initial(sqlite_ws)
        run_alembic(sqlite_ws, "upgrade", "head")
        assert is_up_to_date(sqlite_ws) is True

    def test_is_up_to_date_false_when_pending(self, sqlite_ws):
        _write_initial(sqlite_ws)
        # don't upgrade
        assert is_up_to_date(sqlite_ws) is False

    def test_validate_head_raises_when_pending(self, sqlite_ws):
        _write_initial(sqlite_ws)
        from src.engine.workspace.migrations import validate_head
        with pytest.raises(HeadOutOfSyncError):
            validate_head(sqlite_ws)
