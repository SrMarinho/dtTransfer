import json
import pytest
import signal
from unittest.mock import patch, MagicMock
from src.interfaces.bot.db import init_db
from src.interfaces.bot import jobs
from src.interfaces.bot.commands import stop


@pytest.fixture(autouse=True)
def use_tmp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("BOT_DB_PATH", db_path)
    init_db(db_path)


def test_stop_unknown_hash():
    result = stop.handle(["zzzz"], user_id=1, chat_id="-100abc")
    assert "não encontrado" in result.lower()


def test_stop_non_running_job():
    jobs.create_job("a1b2", "venda", 9999, "-100abc", 1, 10)
    jobs.update_status("a1b2", "done")
    result = stop.handle(["a1b2"], user_id=1, chat_id="-100abc")
    assert "não está rodando" in result.lower()


def test_stop_running_job():
    jobs.create_job("c3d4", "cliente", 9999, "-100abc", 2, 5)
    with patch.object(stop.os, 'kill') as mock_kill:
        result = stop.handle(["c3d4"], user_id=1, chat_id="-100abc")
    mock_kill.assert_called_once_with(9999, signal.SIGTERM)
    assert "parado" in result.lower()
    updated = jobs.get_job("c3d4")
    assert updated.status == "stopped"
