import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.interfaces.bot.db import get_connection, init_db
from src.interfaces.bot import telegram as tg
from src.core.logger.error_parser import get_log_path, parse_errors, build_summary


def _get_last_check() -> Optional[datetime]:
    conn = get_connection()
    row = conn.execute("SELECT value FROM telegram_state WHERE key = 'last_error_check_at'").fetchone()
    conn.close()
    if row:
        try:
            return datetime.fromisoformat(row["value"])
        except Exception:
            pass
    return None


def _set_last_check(ts: datetime) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO telegram_state (key, value) VALUES ('last_error_check_at', ?)",
        (ts.isoformat(timespec="seconds"),),
    )
    conn.commit()
    conn.close()


def main() -> None:
    init_db()

    now = datetime.now()
    last = _get_last_check()

    table_errors: dict = defaultdict(list)
    generic_errors: list = []

    if last and last.date() < now.date():
        t_err, g_err = parse_errors(get_log_path(last), since=last)
        for k, v in t_err.items():
            table_errors[k].extend(v)
        generic_errors.extend(g_err)

    t_err, g_err = parse_errors(get_log_path(now), since=last)
    for k, v in t_err.items():
        table_errors[k].extend(v)
    generic_errors.extend(g_err)

    _set_last_check(now)

    if not table_errors and not generic_errors:
        return

    since_str = last.strftime("%H:%M") if last else "início"
    period = f"{since_str} → {now.strftime('%H:%M')}"
    summary = build_summary(period, table_errors, generic_errors, use_html=True)

    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if chat_id:
        tg.send_long_message(chat_id, summary, parse_mode="HTML")


if __name__ == "__main__":
    main()
