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


app = typer.Typer(help="Gerencia migrations de schema (Alembic) por workspace")


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
    revision: Annotated[str, typer.Option("--revision", help="Revisão alvo")] = "head",
):
    """Aplica migrations pendentes (default: head)."""
    ws = _resolve_workspace(workspace)
    run_alembic(ws, "upgrade", revision)


@app.command("status")
def migrate_status(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
):
    """Mostra revisão atual e última disponível."""
    ws = _resolve_workspace(workspace)
    typer.echo(f"workspace: {ws.id}")
    typer.echo(f"current:   {current_head(ws)}")
    typer.echo(f"available: {available_head(ws)}")
    typer.echo(f"in sync:   {is_up_to_date(ws)}")


@app.command("rollback")
def migrate_rollback(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
    steps: Annotated[int, typer.Option("--steps", help="Quantos migrations desfazer")] = 1,
):
    """Desfaz os últimos N migrations."""
    ws = _resolve_workspace(workspace)
    run_alembic(ws, "downgrade", f"-{steps}")


@app.command("stamp")
def migrate_stamp(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
    revision: Annotated[str, typer.Argument(help="Revisão para marcar (ex: head)")] = "head",
):
    """Marca revisão como aplicada sem rodar SQL."""
    ws = _resolve_workspace(workspace)
    run_alembic(ws, "stamp", revision)


@app.command("create")
def migrate_create(
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Workspace id")],
    message: Annotated[str, typer.Option("--message", "-m", help="Mensagem da migration")] = None,
    autogenerate: Annotated[bool, typer.Option("--autogenerate", help="Detectar mudanças comparando com DB")] = False,
    sql: Annotated[bool, typer.Option("--sql", help="Apenas gerar SQL, não aplicar")] = False,
):
    """Cria nova migration. Use --autogenerate para detectar mudanças no schema."""
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
    """Falha se DB não estiver no head atual."""
    ws = _resolve_workspace(workspace)
    try:
        validate_head(ws)
        typer.secho("OK", fg=typer.colors.GREEN)
    except HeadOutOfSyncError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(2)
