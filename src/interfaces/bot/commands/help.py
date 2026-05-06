_HELP = """\
Comandos disponíveis:

/run <tabela> [opções]   — dispara um job ETL
/stop <hash>             — interrompe um job em execução
/jobs [-n N]             — lista os últimos jobs
/status [opções]         — erros do log do dia
/help                    — esta mensagem

Use /comando --help para detalhes de cada comando.\
"""


def handle(args: list, user_id: int, chat_id: str) -> str:
    return _HELP
