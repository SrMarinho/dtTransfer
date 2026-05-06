"""ETL engine CLI entry point.

Command structure (kubectl-style subcommand groups):
    workspace list|validate|new|delete|restore
    entity    list|new|delete|restore|validate
    migrate   upgrade|status|validate|create|stamp|rollback
    load      full|incremental|monthly|unit
    logs      errors
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import typer

from src.engine.workspace.bootstrap import bootstrap

bootstrap()

from src.interfaces.cli.groups.workspace import app as workspace_app
from src.interfaces.cli.groups.entity import app as entity_app
from src.interfaces.cli.groups.logs import app as logs_app
from src.interfaces.cli.commands.load import app as load_app
from src.interfaces.cli.commands.migrate import app as migrate_app


app = typer.Typer(help="Declarative ETL engine", no_args_is_help=True)

app.add_typer(workspace_app, name="workspace", help="Manage workspaces (list, validate, new, delete, restore)")
app.add_typer(entity_app, name="entity", help="Manage entities (list, new, delete, restore, validate)")
app.add_typer(migrate_app, name="migrate", help="Alembic migrations per workspace")
app.add_typer(load_app, name="load", help="Run ETL processes (full, incremental, monthly, unit)")
app.add_typer(logs_app, name="logs", help="Inspect logs (errors)")

if __name__ == "__main__":
    app()
