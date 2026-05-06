import os
import signal
from datetime import datetime
from src.interfaces.bot import jobs

_HELP = """\
/stop <hash> — interrompe um job em execução

Argumentos:
  hash        identificador do job (ex: a3f2) — veja /jobs
  --help, -h  exibe esta ajuda\
"""


def handle(args: list, user_id: int, chat_id: str) -> str:
    if "--help" in args or "-h" in args:
        return _HELP

    if not args:
        return "❌ Uso: /stop <hash>"

    hash_ = args[0]
    job = jobs.get_job(hash_)

    if not job:
        return f"❌ Job '{hash_}' não encontrado."

    if job.status != "running":
        return f"❌ Job '{hash_}' não está rodando (status: {job.status})."

    try:
        os.kill(job.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    jobs.update_status(hash_, "stopped", ended_at=datetime.now().isoformat(timespec="seconds"))
    return f"🛑 Job {hash_} — {job.label} parado."
