import json
import secrets
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from src.interfaces.bot.db import get_connection


@dataclass
class Job:
    id: int
    hash: str
    label: str
    pid: int
    status: str
    chat_id: str
    message_id: int
    progress: Optional[str]
    last_progress: Optional[str]
    started_at: str
    ended_at: Optional[str]


def _row_to_job(row) -> Job:
    return Job(
        id=row["id"],
        hash=row["hash"],
        label=row["label"],
        pid=row["pid"],
        status=row["status"],
        chat_id=row["chat_id"],
        message_id=row["message_id"],
        progress=row["progress"],
        last_progress=row["last_progress"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
    )


def generate_hash() -> str:
    return secrets.token_hex(2)


def check_rate_limit(user_id: int, command: str, limit_seconds: int = 60) -> bool:
    """Returns True if allowed, False if rate-limited."""
    now = datetime.now()
    with closing(get_connection()) as conn:
        conn.isolation_level = None  # enable manual transaction control
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT last_at FROM rate_limit WHERE user_id = ? AND command = ?",
            (user_id, command),
        ).fetchone()
        if row:
            last_at = datetime.fromisoformat(row["last_at"])
            if now - last_at < timedelta(seconds=limit_seconds):
                conn.execute("ROLLBACK")
                return False
        conn.execute(
            "INSERT OR REPLACE INTO rate_limit (user_id, command, last_at) VALUES (?, ?, ?)",
            (user_id, command, now.isoformat()),
        )
        conn.execute("COMMIT")
    return True


def create_job(hash: str, label: str, pid: int, chat_id: str, message_id: int, total: int) -> Job:
    started_at = datetime.now().isoformat(timespec="seconds")
    progress = json.dumps({"current": 0, "total": total})
    with closing(get_connection()) as conn:
        conn.execute(
            """INSERT INTO jobs (hash, label, pid, status, chat_id, message_id, progress, started_at)
               VALUES (?, ?, ?, 'running', ?, ?, ?, ?)""",
            (hash, label, pid, chat_id, message_id, progress, started_at),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM jobs WHERE hash = ?", (hash,)).fetchone()
    return _row_to_job(row)


def get_job(hash: str) -> Optional[Job]:
    with closing(get_connection()) as conn:
        row = conn.execute("SELECT * FROM jobs WHERE hash = ?", (hash,)).fetchone()
    return _row_to_job(row) if row else None


def update_progress(hash: str, current: int, total: int) -> None:
    progress = json.dumps({"current": current, "total": total})
    with closing(get_connection()) as conn:
        conn.execute("UPDATE jobs SET progress = ? WHERE hash = ?", (progress, hash))
        conn.commit()


def mark_progress_sent(hash: str, progress_json: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute("UPDATE jobs SET last_progress = ? WHERE hash = ?", (progress_json, hash))
        conn.commit()


def update_status(hash: str, status: str, ended_at: Optional[str] = None) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, ended_at = ? WHERE hash = ?",
            (status, ended_at, hash),
        )
        conn.commit()


def list_jobs(limit: int = 10) -> "list[Job]":
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_row_to_job(r) for r in rows]
