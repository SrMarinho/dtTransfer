import subprocess
import sys
import os
from typing import Callable
from src.factories.entity_registry import EntityRegistry
from src.interfaces.bot import jobs

_VALID_PROCESSES = {"regular", "nDaysAgo", "nMonthsAgo", "perUnit"}
_RUNNER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runner.py")

_HELP = """\
/run <tabela> [opções] — dispara um job ETL

Argumentos:
  tabela                    nome da tabela (obrigatório)

Opções:
  --process <nome>          regular | nDaysAgo | nMonthsAgo | perUnit (padrão: regular)
  --days N                  dias atrás (obrigatório para nDaysAgo)
  --months N                meses atrás (obrigatório para nMonthsAgo)
  --threads N               threads paralelas
  --truncate                truncar tabela antes de inserir
  --help, -h                exibe esta ajuda

Exemplos:
  /run venda --process nDaysAgo --days 10 --threads 4
  /run cliente --truncate\
"""


def _make_label(table: str, process: str, days: str, months: str) -> str:
    if days:
        return f"{table} (nDaysAgo, {days} dias)"
    if months:
        return f"{table} (nMonthsAgo, {months} meses)"
    return f"{table} ({process})"


def _make_total(process: str, days: str, months: str) -> int:
    if process == "nDaysAgo" and days:
        return int(days)
    if process == "nMonthsAgo" and months:
        return int(months)
    return 1


def handle(args: list, user_id: int, chat_id: str, reply_fn: Callable) -> str:
    if "--help" in args or "-h" in args:
        return _HELP

    if not jobs.check_rate_limit(user_id, "/run", limit_seconds=60):
        return "⏳ Aguarde 1 minuto antes de disparar outro /run."

    if not args:
        return "❌ Uso: /run <tabela> [--process nDaysAgo] [--days N] [--months N] [--threads N] [--truncate]"

    table = args[0]
    valid = EntityRegistry.valid_tables()
    if table not in valid:
        return f"❌ Tabela inválida: '{table}'"

    process = "regular"
    days = months = threads = None
    truncate = False

    i = 1
    while i < len(args):
        if args[i] == "--process" and i + 1 < len(args):
            process = args[i + 1]; i += 2
        elif args[i] == "--days" and i + 1 < len(args):
            days = args[i + 1]; i += 2
        elif args[i] == "--months" and i + 1 < len(args):
            months = args[i + 1]; i += 2
        elif args[i] == "--threads" and i + 1 < len(args):
            threads = args[i + 1]; i += 2
        elif args[i] == "--truncate":
            truncate = True; i += 1
        else:
            i += 1

    if process not in _VALID_PROCESSES:
        return f"❌ Processo inválido: '{process}'. Válidos: {', '.join(sorted(_VALID_PROCESSES))}"

    if process == "nDaysAgo" and not days:
        return "❌ --days é obrigatório para nDaysAgo. Ex: /run venda --process nDaysAgo --days 10"

    if process == "nMonthsAgo" and not months:
        return "❌ --months é obrigatório para nMonthsAgo. Ex: /run venda --process nMonthsAgo --months 4"

    for name, val in [("--days", days), ("--months", months), ("--threads", threads)]:
        if val is not None:
            try:
                if int(val) <= 0:
                    raise ValueError
            except ValueError:
                return f"❌ {name} deve ser um inteiro positivo."

    job_hash = jobs.generate_hash()
    label = _make_label(table, process, days, months)
    total = _make_total(process, days, months)

    cmd = [sys.executable, _RUNNER, "--hash", job_hash, "--table", table, "--process", process]
    if days:
        cmd += ["--days", days]
    if months:
        cmd += ["--months", months]
    if threads:
        cmd += ["--threads", threads]
    if truncate:
        cmd.append("--truncate")

    proc = subprocess.Popen(cmd, start_new_session=True)

    message_id = reply_fn(f"⏳ {job_hash} — {label}\nProgresso: 0/{total}\nIniciado: aguardando...")
    jobs.create_job(
        hash=job_hash, label=label, pid=proc.pid,
        chat_id=chat_id, message_id=message_id, total=total,
    )
    return ""
