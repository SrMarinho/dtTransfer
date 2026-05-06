import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.logger.telegram_handler import send_telegram
import json
import urllib.request

load_dotenv()

COMMANDS = [
    {"command": "help",   "description": "Lista todos os comandos disponíveis"},
    {"command": "status", "description": "Erros do log de hoje"},
    {"command": "jobs",   "description": "Lista os últimos jobs e seus status"},
    {"command": "run",    "description": "Dispara um job ETL: /run <tabela> [opções]"},
    {"command": "stop",   "description": "Interrompe um job: /stop <hash>"},
]


def set_commands(token: str) -> None:
    payload = json.dumps({"commands": COMMANDS}).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/setMyCommands",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    if result.get("ok"):
        print("Commands registered successfully.")
    else:
        print(f"Error: {result}")


if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        sys.exit(1)
    set_commands(token)
