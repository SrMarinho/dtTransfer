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


app = typer.Typer(help="Manage workspaces (list, validate, new, delete, restore)")


@app.command("list")
def workspace_list(
    deleted: Annotated[bool, typer.Option("--deleted", help="List deleted workspaces")] = False,
):
    """List active or deleted workspaces (--deleted)."""
    if deleted:
        items = list_deleted_workspaces()
        if not items:
            typer.secho("No workspaces in recycle bin.", fg=typer.colors.YELLOW)
            return
        typer.secho(f"Deleted workspaces ({len(items)}):", fg=typer.colors.GREEN, bold=True)
        for item in items:
            dt = item["deleted_at"][:19] if item["deleted_at"] else item["ts"]
            typer.echo(f"  {item['id']:<20}  {dt}  {item['path']}")
        return

    bootstrap()
    items = WorkspaceRegistry().list()
    if not items:
        typer.secho("No workspaces registered.", fg=typer.colors.YELLOW)
        return
    typer.secho(f"Workspaces ({len(items)}):", fg=typer.colors.GREEN, bold=True)
    for ws in items:
        typer.echo(f"  - {ws.id}  [{ws.kind.value}]  {ws.root_path}")


@app.command("validate")
def workspace_validate():
    """Test connections for all workspaces (YAML + legacy)."""
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
    workspace_id: Annotated[str, typer.Argument(help="Workspace id (slug)")],
    driver: Annotated[str, typer.Option("--driver", help="Target database driver")] = "sqlite",
    env_prefix: Annotated[str, typer.Option("--env-prefix", help="Environment variable prefix")] = None,
):
    """Create YAML workspace structure at src/workspaces/<id>/."""
    from src.engine.scaffold import create_workspace
    path = create_workspace(workspace_id, driver=driver, env_prefix=env_prefix)
    typer.secho(f"Workspace created: {path}", fg=typer.colors.GREEN)
    typer.echo("  workspace.yml")
    typer.echo("  entities/")
    typer.echo("  sqls/")
    typer.echo("  migrations/")
    typer.echo("")
    typer.echo(f"Next: python run.py entity new {workspace_id}/<name>")


@app.command("delete")
def workspace_delete(
    workspace_id: Annotated[str, typer.Argument(help="Workspace id")],
    hard: Annotated[bool, typer.Option("--hard", help="Permanently remove")] = False,
):
    """Delete workspace (soft delete: moves to .local/recycle_bin/)."""
    from src.factories.entity_registry import EntityRegistry

    bootstrap()
    try:
        ws = WorkspaceRegistry().get(workspace_id)
    except Exception:
        typer.secho(f"Workspace '{workspace_id}' not found.", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    if hard:
        hard_delete_workspace(ws)
        WorkspaceRegistry().remove(workspace_id)
        typer.secho(f"Workspace '{workspace_id}' permanently removed.", fg=typer.colors.GREEN)
    else:
        dest = soft_delete_workspace(ws)
        WorkspaceRegistry().remove(workspace_id)
        EntityRegistry.remove_entity_prefix(workspace_id)
        typer.secho(
            f"Workspace '{workspace_id}' moved to {dest}",
            fg=typer.colors.GREEN,
        )
        typer.echo("  Use --hard to permanently remove.")
        typer.echo(f"  Use run.py workspace restore {workspace_id} to recover.")


@app.command("restore")
def workspace_restore(
    workspace_id: Annotated[str, typer.Argument(help="Workspace id")],
    ts: Annotated[str, typer.Option("--ts", help="Specific timestamp (YYYYMMDD_HHMMSS)")] = None,
):
    """Restore a deleted workspace from the recycle bin."""
    try:
        dest = restore_workspace(workspace_id, timestamp=ts)
    except FileNotFoundError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except FileExistsError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    typer.secho(f"Workspace '{workspace_id}' restored to {dest}", fg=typer.colors.GREEN)



