import typer
from typing_extensions import Annotated
from src.factories.entity_registry import EntityRegistry

app = typer.Typer(help="Lista tabelas registradas")


@app.command()
def list_tables(
    system: Annotated[str, typer.Option("--system", "-s", help="(deprecated) usar --workspace")] = None,
    workspace: Annotated[str, typer.Option("--workspace", "-w", help="Filtra por workspace id")] = None,
):
    """Lista todas as tabelas registradas no EntityRegistry."""
    tables = EntityRegistry.list_tables(system=workspace or system)
    if not tables:
        typer.secho("Nenhuma tabela encontrada.", fg=typer.colors.YELLOW)
        return
    typer.secho(f"Tabelas registradas ({len(tables)}):", fg=typer.colors.GREEN, bold=True)
    for t in tables:
        typer.echo(f"  - {t}")
