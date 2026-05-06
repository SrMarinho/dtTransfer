import json
from contextlib import closing
from datetime import datetime, timedelta
from src.interfaces.bot.db import get_connection
from src.interfaces.bot.telegram import get_chat_administrators

_CACHE_MINUTES = 5


def _cache_key(chat_id: str) -> str:
    return f"admin_cache_{chat_id}"


def _get_cached_admins(chat_id: str):
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT value FROM telegram_state WHERE key = ?", (_cache_key(chat_id),)
        ).fetchone()
    if not row:
        return None
    data = json.loads(row["value"])
    cached_at = datetime.fromisoformat(data["cached_at"])
    if datetime.now() - cached_at > timedelta(minutes=_CACHE_MINUTES):
        return None
    return data["admin_ids"]


def _set_cached_admins(chat_id: str, admin_ids: list) -> None:
    value = json.dumps({"admin_ids": admin_ids, "cached_at": datetime.now().isoformat()})
    with closing(get_connection()) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO telegram_state (key, value) VALUES (?, ?)",
            (_cache_key(chat_id), value),
        )
        conn.commit()


def is_admin(user_id: int, chat_id: str) -> bool:
    cached = _get_cached_admins(chat_id)
    if cached is not None:
        return user_id in cached
    admins = get_chat_administrators(chat_id)
    admin_ids = [a["user"]["id"] for a in admins]
    _set_cached_admins(chat_id, admin_ids)
    return user_id in admin_ids
