import json
import pytest
from unittest.mock import patch
from src.interfaces.bot.db import init_db
from src.interfaces.bot.auth import is_admin


@pytest.fixture(autouse=True)
def use_tmp_db(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("BOT_DB_PATH", db_path)
    init_db(db_path)


def _mock_admins(user_ids: list):
    return [{"user": {"id": uid}} for uid in user_ids]


def test_is_admin_returns_true_for_admin():
    with patch("src.interfaces.bot.auth.get_chat_administrators", return_value=_mock_admins([111, 222])):
        assert is_admin(user_id=111, chat_id="-100abc") is True


def test_is_admin_returns_false_for_non_admin():
    with patch("src.interfaces.bot.auth.get_chat_administrators", return_value=_mock_admins([111])):
        assert is_admin(user_id=999, chat_id="-100abc") is False


def test_is_admin_uses_cache_on_second_call():
    with patch("src.interfaces.bot.auth.get_chat_administrators", return_value=_mock_admins([111])) as mock_api:
        is_admin(user_id=111, chat_id="-100abc")
        is_admin(user_id=111, chat_id="-100abc")
        assert mock_api.call_count == 1
