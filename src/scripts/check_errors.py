import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.logger.telegram_handler import send_telegram
from src.core.logger.error_parser import get_log_path, parse_errors, build_summary

load_dotenv()


def _parse_dt(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")


def main():
    parser = argparse.ArgumentParser(description='Verifica erros de tabelas nos logs do dataReplicator.')
    parser.add_argument('--date', type=str, default=None,
                        help='Data no formato YYYY-MM-DD (padrão: hoje)')
    parser.add_argument('--days-ago', type=int, default=None,
                        help='Quantos dias atras (ex: 1 = ontem)')
    parser.add_argument('--since', type=str, default=None, metavar='HH:MM',
                        help='Hora de início do intervalo (ex: 08:00)')
    parser.add_argument('--until', type=str, default=None, metavar='HH:MM',
                        help='Hora de fim do intervalo (ex: 17:00)')
    parser.add_argument('--detailed', action='store_true',
                        help='Exibe as mensagens de erro completas')
    args = parser.parse_args()

    if args.date:
        date = datetime.strptime(args.date, '%Y-%m-%d')
    elif args.days_ago is not None:
        date = datetime.now() - timedelta(days=args.days_ago)
    else:
        date = datetime.now()

    date_str_key = date.strftime('%Y-%m-%d')
    since: datetime | None = _parse_dt(date_str_key, args.since) if args.since else None
    until: datetime | None = _parse_dt(date_str_key, args.until) if args.until else None

    table_errors: dict = defaultdict(list)
    generic_errors: list = []

    if since and since.date() < date.date():
        t, g = parse_errors(get_log_path(since), since=since, until=until)
        for k, v in t.items():
            table_errors[k].extend(v)
        generic_errors.extend(g)

    t, g = parse_errors(get_log_path(date), since=since, until=until)
    for k, v in t.items():
        table_errors[k].extend(v)
    generic_errors.extend(g)

    if not table_errors and not generic_errors:
        since_s = args.since or "00:00"
        until_s = args.until or date.strftime("%H:%M")
        print(f"[{date.strftime('%d/%m/%Y')} {since_s}→{until_s}] Nenhum erro encontrado.")
        return

    since_s = args.since or "00:00"
    until_s = args.until or date.strftime("%H:%M")
    period = f"{date.strftime('%d/%m/%Y')} {since_s}→{until_s}"

    summary = build_summary(period, table_errors, generic_errors, detailed=args.detailed)
    print(summary)

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        summary_html = build_summary(period, table_errors, generic_errors, detailed=args.detailed, use_html=True)
        send_telegram(token, chat_id, summary_html, parse_mode="HTML")


if __name__ == "__main__":
    main()
