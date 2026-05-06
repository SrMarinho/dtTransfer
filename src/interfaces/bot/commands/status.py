from src.core.logger.error_parser import parse_errors, build_summary, get_log_path
from datetime import datetime, timedelta

_HELP = """\
/status — erros do log do dia

Opções:
  --date YYYY-MM-DD   data específica
  --days-ago N        N dias atrás (ex: 1 = ontem)
  --detailed          exibe as mensagens de erro completas
  --help, -h          exibe esta ajuda\
"""


def handle(args: list, user_id: int, chat_id: str) -> str:
    if "--help" in args or "-h" in args:
        return _HELP

    date = datetime.now()
    detailed = False

    i = 0
    while i < len(args):
        if args[i] == "--date" and i + 1 < len(args):
            try:
                date = datetime.strptime(args[i + 1], "%Y-%m-%d")
            except ValueError:
                return "❌ Data inválida. Use YYYY-MM-DD."
            i += 2
        elif args[i] == "--days-ago" and i + 1 < len(args):
            try:
                date = datetime.now() - timedelta(days=int(args[i + 1]))
            except ValueError:
                return "❌ --days-ago deve ser um inteiro."
            i += 2
        elif args[i] == "--detailed":
            detailed = True
            i += 1
        else:
            i += 1

    log_path = get_log_path(date)
    table_errors, generic_errors = parse_errors(log_path)

    if not table_errors and not generic_errors:
        return f"✅ Nenhum erro em {date.strftime('%d/%m/%Y')}"

    return build_summary(date.strftime("%d/%m/%Y"), table_errors, generic_errors, detailed=detailed)
