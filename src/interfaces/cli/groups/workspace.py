"""`workspace` command group: list, validate, new, delete, restore."""

import typer
from typing_extensions import Annotated

from src.engine.workspace.bootstrap import bootstrap
from src.engine.workspace.registry import WorkspaceRegistry
from src.engine.workspace.recycle_bin import (
    soft_delete_workspace,
    hard_delete_workspace,
    list_deleted_workspaces,
    restore_workspace,
)


app = typer.Typer(help="Gerencia workspaces (list, validate, new, delete, restore)")


@app.command("list")
def workspace_list(
    deleted: Annotated[bool, typer.Option("--deleted", help="Lista workspaces deletados")] = False,
):
    """Lista workspaces ativos ou deletados (--deleted)."""
    if deleted:
        items = list_deleted_workspaces()
        if not items:
            typer.secho("Nenhum workspace na lixeira.", fg=typer.colors.YELLOW)
            return
        typer.secho(f"Workspaces deletados ({len(items)}):", fg=typer.colors.GREEN, bold=True)
        for item in items:
            dt = item["deleted_at"][:19] if item["deleted_at"] else item["ts"]
            typer.echo(f"  {item['id']:<20}  {dt}  {item['path']}")
        return

    bootstrap()
    items = WorkspaceRegistry().list()
    if not items:
        typer.secho("Nenhum workspace registrado.", fg=typer.colors.YELLOW)
        return
    typer.secho(f"Workspaces ({len(items)}):", fg=typer.colors.GREEN, bold=True)
    for ws in items:
        typer.echo(f"  - {ws.id}  [{ws.kind.value}]  {ws.root_path}")


@app.command("validate")
def workspace_validate():
    """Testa conexao com todos os bancos legacy + workspaces YAML."""
    from src.factories.database_factory import DatabaseFactory, Database

    bootstrap()
    failed = []

    # Legacy enum
    for db_enum in [d for d in Database if d != Database.FAKEDATABASE]:
        try:
            db = DatabaseFactory.getInstance(db_enum)
            conn = db.connection()
            cur = conn.cursor()
            if db.driver in ("pgsql", "postgres"):
                cur.execute("SELECT 1")
            elif db.driver == "sqlite":
                cur.execute("SELECT 1")
            else:
                cur.execute("SELECT 1 FROM DUAL")
            cur.fetchone()
            cur.close()
            conn.close()
            typer.secho(f"OK  legacy/{db.name}", fg=typer.colors.GREEN)
        except Exception as e:
            failed.append((f"legacy/{db_enum.name}", str(e)))
            typer.secho(f"ERR legacy/{db_enum.name}: {e}", fg=typer.colors.RED, err=True)

    # Workspace YAML refs
    for ws in WorkspaceRegistry().list():
        for ref in [ws.target] + list(ws.sources):
            label = f"{ws.id}/{ref.name or ref.env_prefix}"
            try:
                db = DatabaseFactory.getInstance((ws.id, ref.name or ref.env_prefix))
                conn = db.connection()
                cur = conn.cursor()
                if ref.driver == "sqlite":
                    cur.execute("SELECT 1")
                elif ref.driver in ("postgres", "pgsql"):
                    cur.execute("SELECT 1")
                else:
                    cur.execute("SELECT 1 FROM DUAL")
                cur.fetchone()
                cur.close()
                conn.close()
                typer.secho(f"OK  {label}", fg=typer.colors.GREEN)
            except Exception as e:
                failed.append((label, str(e)))
                typer.secho(f"ERR {label}: {e}", fg=typer.colors.RED, err=True)

    if failed:
        raise typer.Exit(1)


@app.command("new")
def workspace_new(
    workspace_id: Annotated[str, typer.Argument(help="Id do workspace (slug)")],
    driver: Annotated[str, typer.Option("--driver", help="Driver do target")] = "sqlite",
    env_prefix: Annotated[str, typer.Option("--env-prefix", help="Prefixo das env vars")] = None,
):
    """Cria estrutura de workspace YAML em src/workspaces/<id>/."""
    from src.engine.scaffold import create_workspace
    path = create_workspace(workspace_id, driver=driver, env_prefix=env_prefix)
    typer.secho(f"Workspace criado: {path}", fg=typer.colors.GREEN)
    typer.echo("  workspace.yml")
    typer.echo("  entities/")
    typer.echo("  sqls/")
    typer.echo("  migrations/")
    typer.echo("")
    typer.echo(f"Próximo: python run.py entity new {workspace_id}/<nome>")


@app.command("delete")
def workspace_delete(
    workspace_id: Annotated[str, typer.Argument(help="Id do workspace")],
    hard: Annotated[bool, typer.Option("--hard", help="Remove permanentemente")] = False,
):
    """Deleta um workspace (soft delete: move para .local/recycle_bin/)."""
    from src.factories.entity_registry import EntityRegistry

    bootstrap()
    try:
        ws = WorkspaceRegistry().get(workspace_id)
    except Exception:
        typer.secho(f"Workspace '{workspace_id}' não encontrado.", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    if hard:
        hard_delete_workspace(ws)
        WorkspaceRegistry().remove(workspace_id)
        typer.secho(f"Workspace '{workspace_id}' removido permanentemente.", fg=typer.colors.GREEN)
    else:
        dest = soft_delete_workspace(ws)
        WorkspaceRegistry().remove(workspace_id)
        EntityRegistry.remove_entity_prefix(workspace_id)
        typer.secho(
            f"Workspace '{workspace_id}' movido para {dest}",
            fg=typer.colors.GREEN,
        )
        typer.echo("  Use --hard para remover permanentemente.")
        typer.echo(f"  Use run.py workspace restore {workspace_id} para recuperar.")


@app.command("restore")
def workspace_restore(
    workspace_id: Annotated[str, typer.Argument(help="Id do workspace")],
    ts: Annotated[str, typer.Option("--ts", help="Timestamp específico (YYYYMMDD_HHMMSS)")] = None,
):
    """Restaura um workspace deletado da lixeira."""
    try:
        dest = restore_workspace(workspace_id, timestamp=ts)
    except FileNotFoundError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except FileExistsError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    typer.secho(f"Workspace '{workspace_id}' restaurado para {dest}", fg=typer.colors.GREEN)



