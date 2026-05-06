import sqlite3
import pytest
from src.interfaces.bot.db import get_connection, init_db


def test_init_db_creates_tables(tmp_path):
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall() if not row[0].startswith("sqlite_")}
    conn.close()
    assert tables == {"telegram_state", "jobs", "rate_limit"}


def test_get_connection_has_row_factory(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("BOT_DB_PATH", db_path)
    conn = get_connection()
    assert conn.row_factory is sqlite3.Row
    # verifies auto-init ran (table exists)
    conn.execute("SELECT key, value FROM telegram_state WHERE 1=0")
    conn.close()
