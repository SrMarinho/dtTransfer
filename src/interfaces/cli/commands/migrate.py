import typer
from typing_extensions import Annotated

from src.engine.workspace.bootstrap import bootstrap
from src.engine.workspace.migrations import (
    HeadOutOfSyncError,
    available_head,
    current_head,
    is_up_to_date,
    run_alembic,
    validate_head,
)
from src.engine.workspace.registry import WorkspaceNotFoundError, WorkspaceRegistry


app = typer.Typer(help="Manage schema migrations (Alembic) per workspace")


def _resolve_workspace(workspace: str):
    bootstrap()
    try:
        return WorkspaceRegistry().get(workspace)
    except WorkspaceNotFoundError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command("upgrade")
def migrate_upgrade(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
    revision: Annotated[str, typer.Option("--revision", help="Target revision")] = "head",
):
    """Apply pending migrations (default: head)."""
    ws = _resolve_workspace(workspace)
    run_alembic(ws, "upgrade", revision)


@app.command("status")
def migrate_status(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
):
    """Show current and latest available revision."""
    ws = _resolve_workspace(workspace)
    typer.echo(f"workspace: {ws.id}")
    typer.echo(f"current:   {current_head(ws)}")
    typer.echo(f"available: {available_head(ws)}")
    typer.echo(f"in sync:   {is_up_to_date(ws)}")


@app.command("rollback")
def migrate_rollback(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
    steps: Annotated[int, typer.Option("--steps", help="Number of migrations to revert")] = 1,
):
    """Roll back last N migrations."""
    ws = _resolve_workspace(workspace)
    run_alembic(ws, "downgrade", f"-{steps}")


@app.command("stamp")
def migrate_stamp(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
    revision: Annotated[str, typer.Argument(help="Revision to stamp (e.g. head)")] = "head",
):
    """Stamp revision as applied without running SQL."""
    ws = _resolve_workspace(workspace)
    run_alembic(ws, "stamp", revision)


@app.command("create")
def migrate_create(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
    message: Annotated[str, typer.Option("--message", "-m", help="Migration message")] = None,
    autogenerate: Annotated[bool, typer.Option("--autogenerate", help="Detect schema changes by comparing with DB")] = False,
    sql: Annotated[bool, typer.Option("--sql", help="Generate SQL only, do not apply")] = False,
):
    """Create a new migration. Use --autogenerate to detect schema changes."""
    ws = _resolve_workspace(workspace)
    opts = {}
    if message:
        opts["message"] = message
    if autogenerate:
        opts["autogenerate"] = True
    if sql:
        opts["sql"] = True
    run_alembic(ws, "revision", **opts)


@app.command("validate")
def migrate_validate(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
):
    """Fail if DB is not at the current head."""
    ws = _resolve_workspace(workspace)
    try:
        validate_head(ws)
        typer.secho("OK", fg=typer.colors.GREEN)
    except HeadOutOfSyncError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(2)
