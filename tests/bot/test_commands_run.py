import pytest
from unittest.mock import patch, MagicMock
from src.interfaces.bot.db import init_db
from src.interfaces.bot.commands import run as run_cmd


@pytest.fixture(autouse=True)
def use_tmp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("BOT_DB_PATH", db_path)
    init_db(db_path)


def test_run_invalid_table():
    with patch.object(run_cmd, 'EntityRegistry') as mock_qf:
        mock_qf.valid_tables.return_value = {"venda", "cliente"}
        result = run_cmd.handle(
            ["tabela_inexistente"], user_id=1, chat_id="-100abc",
            reply_fn=lambda text: None
        )
    assert "inválida" in result.lower()


def test_run_invalid_process():
    with patch.object(run_cmd, 'EntityRegistry') as mock_qf:
        mock_qf.valid_tables.return_value = {"venda"}
        result = run_cmd.handle(
            ["venda", "--process", "processoinvalido"], user_id=1, chat_id="-100abc",
            reply_fn=lambda text: None
        )
    assert "processo inválido" in result.lower()


def test_run_missing_days_for_nDaysAgo():
    with patch.object(run_cmd, 'EntityRegistry') as mock_qf:
        mock_qf.valid_tables.return_value = {"venda"}
        result = run_cmd.handle(
            ["venda", "--process", "nDaysAgo"], user_id=1, chat_id="-100abc",
            reply_fn=lambda text: None
        )
    assert "--days" in result


def test_run_valid_spawns_subprocess():
    with patch.object(run_cmd, 'EntityRegistry') as mock_qf, \
         patch.object(run_cmd.subprocess, 'Popen') as mock_popen, \
         patch.object(run_cmd.jobs, 'create_job') as mock_create:
        mock_qf.valid_tables.return_value = {"venda"}
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_popen.return_value = mock_proc
        mock_create.return_value = MagicMock(hash="a1b2", label="venda (nDaysAgo, 3 dias)")

        result = run_cmd.handle(
            ["venda", "--process", "nDaysAgo", "--days", "3"],
            user_id=1, chat_id="-100abc",
            reply_fn=lambda text: 99,
        )

    mock_popen.assert_called_once()
    args_called = mock_popen.call_args[0][0]
    assert any("runner.py" in str(a) for a in args_called)
    assert "venda" in args_called
    assert "nDaysAgo" in args_called
    assert "3" in args_called

