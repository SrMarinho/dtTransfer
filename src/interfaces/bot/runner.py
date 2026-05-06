import argparse
import logging
import signal
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interfaces.bot import jobs
from src.interfaces.bot.db import init_db

_process = None


def _close_telegram_handlers() -> None:
    from src.core.logger.telegram_handler import TelegramHandler
    for handler in logging.getLogger("dtTransfer").handlers:
        if isinstance(handler, TelegramHandler):
            handler.close()

def _handle_sigterm(signum, frame):
    if _process is not None and hasattr(_process, '_stop'):
        _process._stop.set()
    sys.exit(0)

signal.signal(signal.SIGTERM, _handle_sigterm)

_PROCESSES_WITH_PROGRESS = {"nDaysAgo", "nMonthsAgo"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True)
    parser.add_argument("--table", required=True)
    parser.add_argument("--process", default="regular")
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--months", type=int, default=None)
    parser.add_argument("--threads", type=int, default=None)
    parser.add_argument("--truncate", action="store_true")
    parser.add_argument("--retry-base-delay", type=float, default=30.0)
    parser.add_argument("--retry-max-delay", type=float, default=120.0)
    args = parser.parse_args()

    init_db()

    params = {"table": args.table, "process": args.process}
    if args.days:
        params["days"] = str(args.days)
    if args.months:
        params["months"] = str(args.months)
    if args.threads:
        params["threads"] = str(args.threads)
    if args.truncate:
        params["truncate"] = "True"

    def on_progress(current: int, total: int) -> None:
        jobs.update_progress(args.hash, current, total)

    callback = on_progress if args.process in _PROCESSES_WITH_PROGRESS else None

    global _process
    try:
        if args.process == "nDaysAgo":
            from processes.ndays_ago import nDaysAgo
            _process = nDaysAgo(params, on_progress=callback, retry_base_delay=args.retry_base_delay, retry_max_delay=args.retry_max_delay)
            _process.run()
        elif args.process == "nMonthsAgo":
            from processes.nMonths_ago import nMonthsAgo
            _process = nMonthsAgo(params, on_progress=callback, retry_base_delay=args.retry_base_delay, retry_max_delay=args.retry_max_delay)
            _process.run()
        elif args.process == "regular":
            from processes.regular_query import RegularQuery
            RegularQuery(params).run()
        elif args.process == "perUnit":
            from processes.per_unit import PerUnit
            PerUnit(params).run()
        else:
            raise ValueError(f"Processo desconhecido: {args.process}")

        jobs.update_status(args.hash, "done", ended_at=datetime.now().isoformat(timespec="seconds"))
    except Exception as e:
        jobs.update_status(args.hash, "error", ended_at=datetime.now().isoformat(timespec="seconds"))
        raise
    finally:
        _close_telegram_handlers()


if __name__ == "__main__":
    main()
