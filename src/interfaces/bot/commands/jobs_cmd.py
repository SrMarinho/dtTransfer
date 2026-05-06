import json
from datetime import datetime
from src.interfaces.bot import jobs


def _format_job(job) -> str:
    progress_str = ""
    if job.progress:
        p = json.loads(job.progress)
        progress_str = f" · {p['current']}/{p['total']}"

    started = job.started_at[:16].replace("T", " ")

    if job.status == "running":
        icon = "⏳"
        suffix = f"{progress_str} · {started}"
    elif job.status == "done":
        icon = "✅"
        if job.started_at and job.ended_at:
            elapsed = _elapsed(job.started_at, job.ended_at)
            suffix = f" · concluído em {elapsed}"
        else:
            suffix = ""
    elif job.status == "stopped":
        icon = "🛑"
        suffix = f"{progress_str} · parado"
    else:
        icon = "❌"
        suffix = f" · erro · {started}"

    return f"{icon} {job.hash} — {job.label}{suffix}"


def _elapsed(start: str, end: str) -> str:
    try:
        delta = datetime.fromisoformat(end) - datetime.fromisoformat(start)
        mins, secs = divmod(int(delta.total_seconds()), 60)
        return f"{mins}min {secs}s" if mins else f"{secs}s"
    except Exception:
        return ""


_HELP = """\
/jobs — lista os últimos jobs

Opções:
  -n N        número de jobs a exibir (padrão: 10)
  --help, -h  exibe esta ajuda\
"""


def handle(args: list, user_id: int, chat_id: str) -> str:
    if "--help" in args or "-h" in args:
        return _HELP

    limit = 10
    if "-n" in args:
        idx = args.index("-n")
        if idx + 1 < len(args):
            try:
                limit = int(args[idx + 1])
            except ValueError:
                return "❌ -n deve ser um inteiro."

    all_jobs = jobs.list_jobs(limit=limit)
    if not all_jobs:
        return "Nenhum job registrado."
    return "\n".join(_format_job(j) for j in all_jobs)
