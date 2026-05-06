import json
import os
import pytest
from src.interfaces.bot.db import init_db
from src.interfaces.bot import jobs


@pytest.fixture(autouse=True)
def use_tmp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("BOT_DB_PATH", db_path)
    init_db(db_path)


def test_create_and_get_job():
    job = jobs.create_job(
        hash="a1b2",
        label="venda (nDaysAgo, 10 dias)",
        pid=1234,
        chat_id="-100123",
        message_id=42,
        total=10,
    )
    assert job.hash == "a1b2"
    assert job.status == "running"
    assert job.pid == 1234

    fetched = jobs.get_job("a1b2")
    assert fetched.hash == "a1b2"


def test_update_progress():
    jobs.create_job("b2c3", "cliente (regular)", 999, "-100123", 10, 1)
    jobs.update_progress("b2c3", current=1, total=1)
    job = jobs.get_job("b2c3")
    progress = json.loads(job.progress)
    assert progress == {"current": 1, "total": 1}


def test_update_status():
    jobs.create_job("c3d4", "pedidos (nDaysAgo, 5 dias)", 555, "-100123", 20, 5)
    jobs.update_status("c3d4", "done", ended_at="2026-04-23T15:00:00")
    job = jobs.get_job("c3d4")
    assert job.status == "done"
    assert job.ended_at == "2026-04-23T15:00:00"


def test_list_jobs_returns_recent():
    for i in range(3):
        jobs.create_job(f"x{i}y{i}", f"table{i}", i + 100, "-100123", i + 10, 5)
    result = jobs.list_jobs(limit=10)
    assert len(result) == 3


def test_check_rate_limit_allows_first_call():
    assert jobs.check_rate_limit(user_id=1, command="/run") is True


def test_check_rate_limit_blocks_second_call():
    jobs.check_rate_limit(user_id=1, command="/run")
    assert jobs.check_rate_limit(user_id=1, command="/run") is False


def test_mark_progress_sent():
    jobs.create_job("d4e5", "venda", 111, "-100abc", 5, 10)
    jobs.mark_progress_sent("d4e5", '{"current": 2, "total": 10}')
    job = jobs.get_job("d4e5")
    assert job.last_progress == '{"current": 2, "total": 10}'
