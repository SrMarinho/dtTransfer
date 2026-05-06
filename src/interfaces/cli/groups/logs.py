"""`logs` command group: errors (parse log files)."""

import os
from collections import defaultdict
from datetime import datetime, timedelta

import typer
from dotenv import load_dotenv
from typing_extensions import Annotated

from src.core.logger.error_parser import build_summary, get_log_path, parse_errors
from src.core.logger.telegram_handler import send_telegram


load_dotenv()

app = typer.Typer(help="Inspeciona logs (errors)")


def _parse_dt(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


@app.command("errors")
def logs_errors(
    date: Annotated[str, typer.Option("--date", help="Data YYYY-MM-DD")] = None,
    days_ago: Annotated[int, typer.Option("--days-ago", help="Quantos dias atras")] = None,
    since: Annotated[str, typer.Option("--since", help="Hora inicio HH:MM")] = None,
    until: Annotated[str, typer.Option("--until", help="Hora fim HH:MM")] = None,
    detailed: Annotated[bool, typer.Option("--detailed", help="Mensagens completas")] = False,
):
    """Verifica erros nos logs."""
    if date:
        dt = datetime.strptime(date, "%Y-%m-%d")
    elif days_ago is not None:
        dt = datetime.now() - timedelta(days=days_ago)
    else:
        dt = datetime.now()

    date_str_key = dt.strftime("%Y-%m-%d")
    since_dt = _parse_dt(date_str_key, since) if since else None
    until_dt = _parse_dt(date_str_key, until) if until else None

    table_errors = defaultdict(list)
    generic_errors = []

    if since_dt and since_dt.date() < dt.date():
        t, g = parse_errors(get_log_path(since_dt), since=since_dt, until=until_dt)
        for k, v in t.items():
            table_errors[k].extend(v)
        generic_errors.extend(g)

    t, g = parse_errors(get_log_path(dt), since=since_dt, until=until_dt)
    for k, v in t.items():
        table_errors[k].extend(v)
    generic_errors.extend(g)

    if not table_errors and not generic_errors:
        since_s = since or "00:00"
        until_s = until or dt.strftime("%H:%M")
        typer.secho(
            f"[{dt.strftime('%d/%m/%Y')} {since_s}->{until_s}] Nenhum erro encontrado.",
            fg=typer.colors.GREEN,
        )
        return

    since_s = since or "00:00"
    until_s = until or dt.strftime("%H:%M")
    period = f"{dt.strftime('%d/%m/%Y')} {since_s}->{until_s}"

    summary = build_summary(period, table_errors, generic_errors, detailed=detailed)
    typer.echo(summary)

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        summary_html = build_summary(period, table_errors, generic_errors, detailed=detailed, use_html=True)
        send_telegram(token, chat_id, summary_html, parse_mode="HTML")

    raise typer.Exit(1)
