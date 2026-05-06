import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

_GROUP_CHAT_ID = os.getenv("BOT_GROUP_CHAT_ID", "") or os.getenv("TELEGRAM_CHAT_ID", "")

from src.interfaces.bot.db import get_connection, init_db
from src.interfaces.bot.auth import is_admin
from src.interfaces.bot import jobs
from src.interfaces.bot import telegram as tg
from src.interfaces.bot.commands import help as help_cmd
from src.interfaces.bot.commands import status as status_cmd
from src.interfaces.bot.commands import jobs_cmd
from src.interfaces.bot.commands import stop as stop_cmd
from src.interfaces.bot.commands import run as run_cmd
from src.interfaces.bot.commands import start as start_cmd

_COMMANDS = {
    "/help":   help_cmd.handle,
    "/status": status_cmd.handle,
    "/jobs":   jobs_cmd.handle,
    "/stop":   stop_cmd.handle,
}


def _get_offset() -> int:
    conn = get_connection()
    row = conn.execute("SELECT value FROM telegram_state WHERE key = 'offset'").fetchone()
    conn.close()
    return int(row["value"]) if row else 0


def _set_offset(offset: int) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO telegram_state (key, value) VALUES ('offset', ?)",
        (str(offset),),
    )
    conn.commit()
    conn.close()


def _format_progress_message(job) -> str:
    progress_str = "0/?"
    if job.progress:
        p = json.loads(job.progress)
        progress_str = f"{p['current']}/{p['total']}"
    started = job.started_at[:16].replace("T", " ")
    return f"⏳ {job.hash} — {job.label}\nProgresso: {progress_str}\nIniciado: {started}"


def _format_done_message(job) -> str:
    icon = "✅" if job.status == "done" else ("🛑" if job.status == "stopped" else "❌")
    elapsed = ""
    if job.started_at and job.ended_at:
        try:
            delta = datetime.fromisoformat(job.ended_at) - datetime.fromisoformat(job.started_at)
            mins, secs = divmod(int(delta.total_seconds()), 60)
            elapsed = f" · {mins}min {secs}s" if mins else f" · {secs}s"
        except Exception:
            pass
    return f"{icon} {job.hash} — {job.label}{elapsed}"


def _is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def _monitor_jobs() -> None:
    running = [j for j in jobs.list_jobs(limit=50) if j.status == "running"]
    for job in running:
        alive = _is_pid_alive(job.pid)
        if not alive:
            jobs.update_status(job.hash, "done", ended_at=datetime.now().isoformat(timespec="seconds"))
            job = jobs.get_job(job.hash)
            tg.edit_message(job.chat_id, job.message_id, _format_done_message(job))
            continue

        if job.progress != job.last_progress:
            tg.edit_message(job.chat_id, job.message_id, _format_progress_message(job))
            jobs.mark_progress_sent(job.hash, job.progress)


def _handle_update(update: dict) -> None:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    text = message.get("text", "")
    if not text.startswith("/"):
        return

    chat_id = str(message["chat"]["id"])
    user_id = message["from"]["id"]
    chat_type = message["chat"].get("type", "")

    if chat_type == "private":
        if not _GROUP_CHAT_ID or not is_admin(user_id=user_id, chat_id=_GROUP_CHAT_ID):
            return
    else:
        if not is_admin(user_id=user_id, chat_id=chat_id):
            return

    parts = text.split()
    command = parts[0].split("@")[0].lower()
    args = parts[1:]

    if command == "/start":
        start_cmd.handle(args, user_id=user_id, chat_id=chat_id)
        return

    if command == "/run":
        def reply_fn(text: str) -> int:
            return tg.send_message(chat_id, text)
        result = run_cmd.handle(args, user_id=user_id, chat_id=chat_id, reply_fn=reply_fn)
        if result:
            tg.send_message(chat_id, result)
        return

    handler = _COMMANDS.get(command)
    if handler:
        result = handler(args, user_id=user_id, chat_id=chat_id)
        if result:
            tg.send_message(chat_id, result)


def main() -> None:
    init_db()
    offset = _get_offset()

    updates = tg.get_updates(offset)
    for update in updates:
        _handle_update(update)
        offset = update["update_id"] + 1

    if updates:
        _set_offset(offset)

    _monitor_jobs()


if __name__ == "__main__":
    main()
