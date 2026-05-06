"""`entity` command group: list, new, delete, restore, validate."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from src.factories.entity_registry import EntityRegistry
from src.engine.workspace.bootstrap import bootstrap
from src.engine.workspace.recycle_bin import (
    soft_delete_entity,
    hard_delete_entity,
    list_deleted_entities,
    restore_entity,
)


app = typer.Typer(help="Gerencia entidades (list, new, delete, restore, validate)")

# ─── validate sub-group ───────────────────────────────────────────────────

validate_app = typer.Typer(help="Valida entidades (insert)")
app.add_typer(validate_app, name="validate")


@validate_app.command("insert")
def validate_insert(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    values: Annotated[str, typer.Option("--values", "-v", help="Valores separados por delimiter")],
    columns: Annotated[Optional[str], typer.Option("--columns", "-c", help="Nomes das colunas separados por virgula")] = None,
    delimiter: Annotated[str, typer.Option("--delimiter", "-d", help="Separador dos valores")] = ",",
    commit: Annotated[bool, typer.Option("--commit", help="Persiste o INSERT (padrao = ROLLBACK)")] = False,
    notify: Annotated[bool, typer.Option("--notify", help="Notifica via Telegram se --commit")] = False,
    sql_only: Annotated[bool, typer.Option("--sql-only", help="So mostra o SQL, nao executa")] = False,
):
    """Testa INSERT em uma entidade (ROLLBACK por padrao)."""
    if "/" not in qualified:
        raise typer.BadParameter("formato esperado: <workspace>/<entity_name>")

    bootstrap()
    entity = EntityRegistry.getInstance(qualified, {})

    cols = columns.split(",") if columns else entity.columns
    vals = values.split(delimiter)

    if len(cols) != len(vals):
        typer.secho(
            f"ERRO: --columns ({len(cols)}) e --values ({len(vals)}) devem ter o mesmo numero de itens",
            fg=typer.colors.RED, err=True,
        )
        raise typer.Exit(1)

    placeholders = ",".join("%s" for _ in cols)
    sql = f"INSERT INTO {entity.name} ({','.join(cols)}) VALUES ({placeholders})"

    if sql_only:
        typer.echo(f"SQL: {sql}")
        typer.echo(f"Valores: {vals}")
        return

    conn = entity.toDriver.connection()
    cur = conn.cursor()
    ok = True
    msg = ""
    try:
        cur.execute(sql, vals)
        if commit:
            conn.commit()
            msg = f"INSERT confirmado em {qualified}"
            typer.secho(f"OK (COMMIT) em {qualified}", fg=typer.colors.GREEN)
        else:
            conn.rollback()
            msg = f"INSERT valido (ROLLBACK) em {qualified}"
            typer.secho(f"OK (ROLLBACK) em {qualified}", fg=typer.colors.GREEN)
    except Exception as e:
        conn.rollback()
        ok = False
        msg = f"INSERT FALHOU em {qualified}: {e}"
        typer.secho(msg, fg=typer.colors.RED, err=True)
    finally:
        cur.close()
        conn.close()

    if commit and notify and os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        _send_telegram_notify(ok, qualified, cols, vals, msg)


def _send_telegram_notify(ok: bool, qualified: str, cols: list, vals: list, msg: str):
    from src.core.logger.telegram_handler import send_telegram
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    icon = "✅" if ok else "❌"
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    text = (
        f"{icon} validate insert {qualified}\n"
        f"   Colunas: {', '.join(cols)}\n"
        f"   Valores: {', '.join(vals)}\n"
        f"   {msg}\n"
        f"   {now}"
    )
    try:
        send_telegram(token, chat_id, text)
    except Exception:
        pass


@app.command("list")
def entity_list(
    workspace: Annotated[str, typer.Argument(help="Workspace id (opcional)")] = None,
    deleted: Annotated[bool, typer.Option("--deleted", help="Lista entidades deletadas")] = False,
):
    """Lista entidades registradas ou deletadas (--deleted)."""
    if deleted:
        items = list_deleted_entities(ws_id=workspace)
        if not items:
            typer.secho("Nenhuma entidade na lixeira.", fg=typer.colors.YELLOW)
            return
        typer.secho(f"Entidades deletadas ({len(items)}):", fg=typer.colors.GREEN, bold=True)
        for item in items:
            dt = item["deleted_at"][:19] if item["deleted_at"] else item["ts"]
            typer.echo(f"  {item['workspace']}/{item['entity']:<30}  {dt}")
        return

    bootstrap()
    tables = EntityRegistry.list_tables(system=workspace)
    if not tables:
        typer.secho("Nenhuma entidade encontrada.", fg=typer.colors.YELLOW)
        return
    typer.secho(f"Entidades registradas ({len(tables)}):", fg=typer.colors.GREEN, bold=True)
    for t in tables:
        typer.echo(f"  - {t}")


@app.command("new")
def entity_new(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    process_type: Annotated[str, typer.Option("--process", "-p", help="full|incremental|monthly|unit")] = "full",
):
    """Cria entity YAML + SQL template em src/workspaces/<ws>/entities/."""
    from src.engine.scaffold import create_entity
    if "/" not in qualified:
        raise typer.BadParameter("formato esperado: <workspace>/<entity_name>")
    ws_id, name = qualified.split("/", 1)
    yml_path, sql_path = create_entity(ws_id, name, process_type=process_type)
    typer.secho(f"Entidade criada:", fg=typer.colors.GREEN)
    typer.echo(f"  {yml_path}")
    typer.echo(f"  {sql_path}")


@app.command("delete")
def entity_delete(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    hard: Annotated[bool, typer.Option("--hard", help="Remove permanentemente")] = False,
):
    """Deleta uma entidade (soft delete: move para .local/recycle_bin/)."""
    if "/" not in qualified:
        raise typer.BadParameter("formato esperado: <workspace>/<entity_name>")
    ws_id, name = qualified.split("/", 1)

    from src.engine.workspace.registry import WorkspaceRegistry
    bootstrap()
    try:
        ws = WorkspaceRegistry().get(ws_id)
    except Exception:
        typer.secho(f"Workspace '{ws_id}' não encontrado.", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    key = qualified
    EntityRegistry.getInstance(key, {})  # raises if not found

    if hard:
        hard_delete_entity(ws_id, name, Path(ws.root_path))
        EntityRegistry.remove_entity(key)
        typer.secho(f"Entidade '{qualified}' removida permanentemente.", fg=typer.colors.GREEN)
    else:
        dest = soft_delete_entity(ws_id, name, Path(ws.root_path))
        EntityRegistry.remove_entity(key)
        typer.secho(
            f"Entidade '{qualified}' movida para {dest}",
            fg=typer.colors.GREEN,
        )
        typer.echo("  Use --hard para remover permanentemente.")
        typer.echo(f"  Use run.py entity restore {qualified} para recuperar.")


@app.command("restore")
def entity_restore(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    ts: Annotated[str, typer.Option("--ts", help="Timestamp específico (YYYYMMDD_HHMMSS)")] = None,
):
    """Restaura uma entidade deletada da lixeira."""
    if "/" not in qualified:
        raise typer.BadParameter("formato esperado: <workspace>/<entity_name>")
    ws_id, name = qualified.split("/", 1)

    try:
        restore_entity(ws_id, name, timestamp=ts)
    except FileNotFoundError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except FileExistsError as e:
        typer.secho(str(e), fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    typer.secho(f"Entidade '{qualified}' restaurada com sucesso.", fg=typer.colors.GREEN)


@app.command("parse")
def entity_parse(
    raw: str = typer.Argument(help="Tupla copiada do erro: (val1, val2, ...) ou texto com tupla"),
):
    """Extrai valores de uma tupla Python para usar no validate insert."""
    import re
    m = re.search(r"\((.+)\)", raw, re.DOTALL)
    if not m:
        typer.secho("Nenhuma tupla encontrada. Use o formato: (val1, val2, ...)", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    inner = m.group(1)
    values = []
    current = ""
    depth = 0
    in_str = False

    for ch in inner:
        if ch == "'" and not in_str:
            in_str = True
            continue
        elif ch == "'" and in_str:
            in_str = False
            continue

        if in_str:
            current += ch
        elif ch == "(":
            depth += 1
            current += ch
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            values.append(current.strip().strip("'"))
            current = ""
        else:
            current += ch

    if current.strip():
        values.append(current.strip().strip("'"))

    parsed = []
    for v in values:
        v = v.strip()
        if v.startswith("datetime.datetime"):
            nums = re.findall(r"\d+", v)
            if len(nums) >= 3:
                v = f"{nums[0]}-{nums[1].zfill(2)}-{nums[2].zfill(2)}"
            else:
                v = ""
        parsed.append(v)

    typer.echo(",".join(parsed))



