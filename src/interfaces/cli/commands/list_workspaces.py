import typer

from src.engine.workspace.bootstrap import bootstrap
from src.engine.workspace.registry import WorkspaceRegistry

app = typer.Typer(help="Lista workspaces disponíveis")


@app.command()
def list_workspaces():
    """Lista todos os workspaces descobertos (built-in + externos)."""
    bootstrap()
    items = WorkspaceRegistry().list()
    if not items:
        typer.secho("Nenhum workspace registrado.", fg=typer.colors.YELLOW)
        return
    typer.secho(f"Workspaces ({len(items)}):", fg=typer.colors.GREEN, bold=True)
    for ws in items:
        typer.echo(f"  - {ws.id}  [{ws.kind.value}]  {ws.root_path}")
