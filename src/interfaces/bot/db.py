import sqlite3
import os
from contextlib import closing
from typing import Optional

_DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".local", "bot.db")


def _db_path() -> str:
    return os.getenv("BOT_DB_PATH", _DEFAULT_DB)


def init_db(path: Optional[str] = None) -> None:
    resolved = path or _db_path()
    os.makedirs(os.path.dirname(resolved), exist_ok=True)
    with closing(sqlite3.connect(resolved)) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS telegram_state (
            key   TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            hash          TEXT UNIQUE,
            label         TEXT,
            pid           INTEGER,
            status        TEXT,
            chat_id       TEXT,
            message_id    INTEGER,
            progress      TEXT,
            last_progress TEXT,
            started_at    TEXT,
            ended_at      TEXT
        );

        CREATE TABLE IF NOT EXISTS rate_limit (
            user_id  INTEGER,
            command  TEXT,
            last_at  TEXT,
            PRIMARY KEY (user_id, command)
        );
    """)
        conn.commit()


def get_connection() -> sqlite3.Connection:
    path = _db_path()
    if not os.path.exists(path):
        init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
