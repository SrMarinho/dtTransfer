"""Scaffold helpers for `workspace new` and `entity new`."""

from pathlib import Path
from typing import Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKSPACES_DIR = REPO_ROOT / "src" / "workspaces"


_WORKSPACE_YML = """\
$schema: ../../../schemas/workspace.json
id: {id}
kind: yaml
enabled: true

target:
  name: target_db
  driver: {driver}
  env_prefix: {env_prefix}

sources:
  - name: source_db
    driver: {driver}
    env_prefix: {env_prefix}_SOURCE
"""


_ENTITY_YML = """\
$schema: ../../../../schemas/entity.json
name: {name}
target_table: {name}
source: source_db
target: target_db
process_type: {process}
sql_file: consulta_{name}.sql
columns:
  - id
  - name
"""


_SQL_TEMPLATE = """\
-- Extraction for entity {name}
-- Use REPLACE_START_DATE / REPLACE_END_DATE for incremental queries.
SELECT
    id,
    name
FROM {name}
WHERE 1=1
"""


_ALEMBIC_INI = """\
[alembic]
script_location = .
sqlalchemy.url = driver://placeholder

[loggers]
keys = root

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
"""


_ALEMBIC_ENV = """\
from logging.config import fileConfig
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    from src.engine.workspace.migrations import build_engine_for_alembic
    connectable = build_engine_for_alembic(context)
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""


class ScaffoldError(Exception):
    pass


def create_workspace(
    workspace_id: str,
    driver: str = "sqlite",
    env_prefix: Optional[str] = None,
) -> Path:
    """Create a new workspace skeleton at src/workspaces/<id>/."""
    if not workspace_id or "/" in workspace_id:
        raise ScaffoldError(f"invalid workspace id: '{workspace_id}'")
    root = WORKSPACES_DIR / workspace_id
    if root.exists():
        raise ScaffoldError(f"workspace already exists: {root}")

    env_prefix = env_prefix or f"DB_{workspace_id.upper()}"

    (root / "entities").mkdir(parents=True)
    (root / "sqls").mkdir()
    (root / "migrations" / "versions").mkdir(parents=True)

    (root / "workspace.yml").write_text(
        _WORKSPACE_YML.format(id=workspace_id, driver=driver, env_prefix=env_prefix),
        encoding="utf-8",
    )
    (root / "migrations" / "alembic.ini").write_text(_ALEMBIC_INI, encoding="utf-8")
    (root / "migrations" / "env.py").write_text(_ALEMBIC_ENV, encoding="utf-8")
    (root / "migrations" / "script.py.mako").write_text(_SCRIPT_MAKO, encoding="utf-8")

    return root


def create_entity(
    workspace_id: str,
    entity_name: str,
    process_type: str = "full",
) -> Tuple[Path, Path]:
    """Create entity YAML + SQL template inside an existing workspace."""
    root = WORKSPACES_DIR / workspace_id
    if not root.exists():
        raise ScaffoldError(
            f"workspace '{workspace_id}' not found at {root}. "
            f"Run: python run.py workspace new {workspace_id}"
        )
    if process_type not in {"full", "incremental", "monthly", "unit"}:
        raise ScaffoldError(f"invalid process_type: {process_type}")

    yml = root / "entities" / f"{entity_name}.yml"
    sql = root / "sqls" / f"consulta_{entity_name}.sql"
    if yml.exists():
        raise ScaffoldError(f"entity already exists: {yml}")

    yml.write_text(
        _ENTITY_YML.format(name=entity_name, process=process_type),
        encoding="utf-8",
    )
    sql.write_text(_SQL_TEMPLATE.format(name=entity_name), encoding="utf-8")
    return yml, sql


_SCRIPT_MAKO = """\
\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

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


__all__ = ["create_workspace", "create_entity", "ScaffoldError"]
