import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.core.logger.telegram_handler import send_telegram

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

if not token or not chat_id:
    print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env")
    sys.exit(1)

env_label = os.getenv("ENV", "production")
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
message = f"✅ dataReplicator — Telegram OK [{env_label}]\n{timestamp}"

try:
    send_telegram(token, chat_id, message)
    print(f"Message sent to chat_id={chat_id}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
