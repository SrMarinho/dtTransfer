import html as _html
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Optional

_HASH_PREFIX = r'(?:\[[a-f0-9]+\] )?'
TABLE_ERROR_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - ERROR - ' + _HASH_PREFIX + r'([a-z][a-z0-9_]{2,}) - (.+)$')
GENERIC_ERROR_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - ERROR - ' + _HASH_PREFIX + r'(.+)$')
CONTEXT_TABLE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - (?:INFO|WARNING|ERROR) - ' + _HASH_PREFIX + r'([a-z][a-z0-9_]{2,}) - ')


def get_log_path(date: datetime) -> str:
    return os.path.join('logs', date.strftime('%Y'), date.strftime('%m'), date.strftime('%Y%m%d') + '.log')


def parse_errors(log_path: str, since: Optional[datetime] = None, until: Optional[datetime] = None) -> tuple:
    table_errors = defaultdict(list)
    generic_errors = []
    current_table: Optional[str] = None

    if not os.path.exists(log_path):
        return table_errors, generic_errors

    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip()

            ctx_match = CONTEXT_TABLE_PATTERN.match(line)
            if ctx_match:
                current_table = ctx_match.group(1)

            table_match = TABLE_ERROR_PATTERN.match(line)
            if table_match:
                ts = datetime.strptime(table_match.group(1), '%Y-%m-%d %H:%M:%S')
                if since and ts <= since:
                    continue
                if until and ts > until:
                    continue
                table_errors[table_match.group(2)].append(table_match.group(3))
            else:
                generic_match = GENERIC_ERROR_PATTERN.match(line)
                if generic_match:
                    ts = datetime.strptime(generic_match.group(1), '%Y-%m-%d %H:%M:%S')
                    if since and ts <= since:
                        continue
                    if until and ts > until:
                        continue
                    msg = generic_match.group(2)
                    if current_table:
                        table_errors[current_table].append(msg)
                    else:
                        generic_errors.append(msg)

    return table_errors, generic_errors


def _severity_icon(count: int) -> str:
    if count >= 5:
        return "🔴"
    if count >= 2:
        return "🟡"
    return "⚪"


def build_summary(date_str: str, table_errors: dict, generic_errors: list, detailed: bool = False, use_html: bool = False) -> str:
    if use_html:
        total = sum(len(v) for v in table_errors.values()) + len(generic_errors)
        lines = [f"❌ <b>dataReplicator</b> — {total} erro(s)\n🕐 {date_str}\n"]

        for table, messages in sorted(table_errors.items()):
            icon = _severity_icon(len(messages))
            lines.append(f"{icon} <b>{_html.escape(table)}</b> — {len(messages)}x")
            for msg in (messages if detailed else messages[:1]):
                lines.append(f"  ↳ {_html.escape(msg[:300])}")
            lines.append("")

        if generic_errors:
            icon = _severity_icon(len(generic_errors))
            lines.append(f"{icon} <b>outros</b> — {len(generic_errors)}x")
            seen: set = set()
            for msg in generic_errors:
                short = _html.escape(msg[:300])
                if short not in seen:
                    lines.append(f"  ↳ {short}")
                    seen.add(short)
                    if not detailed:
                        break

        return "\n".join(lines)

    lines = [f"[ERRO] dataReplicator - Erros em {date_str}\n"]

    for table, messages in sorted(table_errors.items()):
        lines.append(f"  - {table} ({len(messages)}x)")
        if detailed:
            for msg in messages:
                lines.append(f"      {msg[:300]}")

    if generic_errors:
        lines.append(f"  - outros erros ({len(generic_errors)}x)")
        if detailed:
            seen = set()
            for msg in generic_errors:
                short = msg[:300]
                if short not in seen:
                    lines.append(f"      {short}")
                    seen.add(short)

    return "\n".join(lines)
