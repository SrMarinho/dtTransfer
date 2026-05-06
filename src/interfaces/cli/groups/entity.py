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


app = typer.Typer(help="Manage entities (list, new, delete, restore, validate)")

# ─── validate sub-group ───────────────────────────────────────────────────

validate_app = typer.Typer(help="Validate entities (insert)")
app.add_typer(validate_app, name="validate")


@validate_app.command("insert")
def validate_insert(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    values: Annotated[str, typer.Option("--values", "-v", help="Values separated by delimiter")],
    columns: Annotated[Optional[str], typer.Option("--columns", "-c", help="Column names separated by commas")] = None,
    delimiter: Annotated[str, typer.Option("--delimiter", "-d", help="Value delimiter")] = ",",
    commit: Annotated[bool, typer.Option("--commit", help="Persist INSERT (default = ROLLBACK)")] = False,
    notify: Annotated[bool, typer.Option("--notify", help="Notify via Telegram if --commit")] = False,
    sql_only: Annotated[bool, typer.Option("--sql-only", help="Show SQL only, do not execute")] = False,
):
    """Test INSERT on an entity (ROLLBACK by default)."""
    if "/" not in qualified:
        raise typer.BadParameter("expected format: <workspace>/<entity_name>")

    bootstrap()
    entity = EntityRegistry.getInstance(qualified, {})

    cols = columns.split(",") if columns else entity.columns
    vals = values.split(delimiter)

    if len(cols) != len(vals):
        typer.secho(
            f"ERROR: --columns ({len(cols)}) and --values ({len(vals)}) must have the same count",
            fg=typer.colors.RED, err=True,
        )
        raise typer.Exit(1)

    placeholders = ",".join("%s" for _ in cols)
    sql = f"INSERT INTO {entity.name} ({','.join(cols)}) VALUES ({placeholders})"

    if sql_only:
        typer.echo(f"SQL: {sql}")
        typer.echo(f"Values: {vals}")
        return

    conn = entity.toDriver.connection()
    cur = conn.cursor()
    ok = True
    msg = ""
    try:
        cur.execute(sql, vals)
        if commit:
            conn.commit()
            msg = f"INSERT committed on {qualified}"
            typer.secho(f"OK (COMMIT) on {qualified}", fg=typer.colors.GREEN)
        else:
            conn.rollback()
            msg = f"INSERT valid (ROLLBACK) on {qualified}"
            typer.secho(f"OK (ROLLBACK) on {qualified}", fg=typer.colors.GREEN)
    except Exception as e:
        conn.rollback()
        ok = False
        msg = f"INSERT FAILED on {qualified}: {e}"
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
    workspace: Annotated[str, typer.Argument(help="Workspace id (optional)")] = None,
    deleted: Annotated[bool, typer.Option("--deleted", help="List deleted entities")] = False,
):
    """List registered or deleted entities (--deleted)."""
    if deleted:
        items = list_deleted_entities(ws_id=workspace)
        if not items:
            typer.secho("No entities in recycle bin.", fg=typer.colors.YELLOW)
            return
        typer.secho(f"Deleted entities ({len(items)}):", fg=typer.colors.GREEN, bold=True)
        for item in items:
            dt = item["deleted_at"][:19] if item["deleted_at"] else item["ts"]
            typer.echo(f"  {item['workspace']}/{item['entity']:<30}  {dt}")
        return

    bootstrap()
    tables = EntityRegistry.list_tables(system=workspace)
    if not tables:
        typer.secho("No entities found.", fg=typer.colors.YELLOW)
        return
    typer.secho(f"Registered entities ({len(tables)}):", fg=typer.colors.GREEN, bold=True)
    for t in tables:
        typer.echo(f"  - {t}")


@app.command("new")
def entity_new(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    process_type: Annotated[str, typer.Option("--process", "-p", help="full|incremental|monthly|unit")] = "full",
):
    """Create entity YAML + SQL template under src/workspaces/<ws>/entities/."""
    from src.engine.scaffold import create_entity
    if "/" not in qualified:
        raise typer.BadParameter("expected format: <workspace>/<entity_name>")
    ws_id, name = qualified.split("/", 1)
    yml_path, sql_path = create_entity(ws_id, name, process_type=process_type)
    typer.secho(f"Entity created:", fg=typer.colors.GREEN)
    typer.echo(f"  {yml_path}")
    typer.echo(f"  {sql_path}")


@app.command("delete")
def entity_delete(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    hard: Annotated[bool, typer.Option("--hard", help="Permanently remove")] = False,
):
    """Delete entity (soft delete: moves to .local/recycle_bin/)."""
    if "/" not in qualified:
        raise typer.BadParameter("formato esperado: <workspace>/<entity_name>")
    ws_id, name = qualified.split("/", 1)

    from src.engine.workspace.registry import WorkspaceRegistry
    bootstrap()
    try:
        ws = WorkspaceRegistry().get(ws_id)
    except Exception:
        typer.secho(f"Workspace '{ws_id}' not found.", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    key = qualified
    EntityRegistry.getInstance(key, {})  # raises if not found

    if hard:
        hard_delete_entity(ws_id, name, Path(ws.root_path))
        EntityRegistry.remove_entity(key)
        typer.secho(f"Entity '{qualified}' permanently removed.", fg=typer.colors.GREEN)
    else:
        dest = soft_delete_entity(ws_id, name, Path(ws.root_path))
        EntityRegistry.remove_entity(key)
        typer.secho(
            f"Entity '{qualified}' moved to {dest}",
            fg=typer.colors.GREEN,
        )
        typer.echo("  Use --hard to permanently remove.")
        typer.echo(f"  Use run.py entity restore {qualified} to recover.")


@app.command("restore")
def entity_restore(
    qualified: Annotated[str, typer.Argument(help="<workspace>/<entity_name>")],
    ts: Annotated[str, typer.Option("--ts", help="Specific timestamp (YYYYMMDD_HHMMSS)")] = None,
):
    """Restore a deleted entity from the recycle bin."""
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
    typer.secho(f"Entity '{qualified}' restored successfully.", fg=typer.colors.GREEN)


@app.command("parse")
def entity_parse(
    raw: str = typer.Argument(help="Tuple copied from error: (val1, val2, ...)"),
):
    """Extract values from a Python tuple for use with validate insert."""
    import re
    m = re.search(r"\((.+)\)", raw, re.DOTALL)
    if not m:
        typer.secho("No tuple found. Use format: (val1, val2, ...)", fg=typer.colors.RED, err=True)
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



