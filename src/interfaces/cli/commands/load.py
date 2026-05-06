import typer
from typing import Optional
from typing_extensions import Annotated
from src.factories.mode_factory import ModeFactory
from src.factories.process_factory import ProcessFactory
from src.factories.entity_registry import EntityRegistry
from src.core.logger.run_context import set_run_hash
from src.core.logger.logging import logger
from src.interfaces.cli.validators import validate_table

app = typer.Typer(help="Executa processos ETL")


def _resolve_table(table: str, workspace: Optional[str]) -> str:
    if workspace and "/" not in table:
        return f"{workspace}/{table}"
    return table


def _run_process(process_name: str, table: str, params: dict, workspace: Optional[str] = None):
    run_hash = set_run_hash()
    qualified = _resolve_table(table, workspace)
    logger.info(f"run={run_hash} workspace={workspace} table={qualified} process={process_name}")
    params["mode"] = "cli"
    params["process"] = process_name
    params["table"] = qualified
    params["workspace"] = workspace
    mode = ModeFactory.getInstance("cli", params)
    mode.run()


@app.command("full")
def load_full(
    table: Annotated[str, typer.Option("--table", "-t", help="Nome da tabela/entidade")],
    workspace: Annotated[Optional[str], typer.Option("--workspace", "-w", help="Workspace id")] = None,
    truncate: Annotated[bool, typer.Option("--truncate", help="Truncar tabela destino antes de inserir")] = False,
):
    """Sincronizacao completa de tabela (truncate + load)."""
    params = {"truncate": truncate}
    _run_process("full", table, params, workspace)


@app.command("incremental")
def load_incremental(
    table: Annotated[str, typer.Option("--table", "-t", help="Nome da tabela/entidade")],
    workspace: Annotated[Optional[str], typer.Option("--workspace", "-w", help="Workspace id")] = None,
    days: Annotated[Optional[int], typer.Option("--days", "-d", help="Quantidade de dias atras", min=1)] = None,
    threads: Annotated[int, typer.Option("--threads", help="Numero de threads paralelas", min=1, max=50)] = 4,
    truncate: Annotated[bool, typer.Option("--truncate", help="Truncar tabela destino")] = False,
    current_day: Annotated[bool, typer.Option("--current-day", help="Incluir o dia atual na sincronizacao")] = False,
    full: Annotated[bool, typer.Option("--full", help="Full load sem filtro de data (ignora --days)")] = False,
):
    """Sincronizacao incremental pelos ultimos N dias (multithreading). Use --full para carga completa."""
    if not full and days is None:
        raise typer.BadParameter("--days e obrigatorio quando --full nao e usado.")
    params = {
        "days": days,
        "threads": threads,
        "truncate": truncate,
        "currentDay": current_day,
        "full": full,
    }
    _run_process("incremental", table, params, workspace)


@app.command("monthly")
def load_monthly(
    table: Annotated[str, typer.Option("--table", "-t", help="Nome da tabela/entidade")],
    workspace: Annotated[Optional[str], typer.Option("--workspace", "-w", help="Workspace id")] = None,
    months: Annotated[Optional[int], typer.Option("--months", "-m", help="Quantidade de meses atras", min=1)] = None,
    method: Annotated[str, typer.Option("--method", help="Metodo: byMonth ou wholeInterval")] = "byMonth",
    truncate: Annotated[bool, typer.Option("--truncate", help="Truncar tabela destino")] = False,
    full: Annotated[bool, typer.Option("--full", help="Full load sem filtro de data (ignora --months)")] = False,
):
    """Sincronizacao incremental pelos ultimos N meses. Use --full para carga completa."""
    if not full and months is None:
        raise typer.BadParameter("--months e obrigatorio quando --full nao e usado.")
    params = {
        "months": months,
        "method": method,
        "truncate": truncate,
        "full": full,
    }
    _run_process("monthly", table, params, workspace)


@app.command("unit")
def load_unit(
    table: Annotated[str, typer.Option("--table", "-t", help="Nome da tabela/entidade")],
    workspace: Annotated[Optional[str], typer.Option("--workspace", "-w", help="Workspace id")] = None,
    unit: Annotated[int, typer.Option("--unit", "-u", help="ID da unidade/CD")] = 0,
):
    """Sincronizacao de dados para uma unidade especifica."""
    params = {"unit": unit}
    _run_process("unit", table, params, workspace)
