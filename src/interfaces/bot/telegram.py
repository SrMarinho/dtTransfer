import json
import os
import urllib.request
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
_BASE = f"https://api.telegram.org/bot{_TOKEN}"
_MAX_LENGTH = 4096


def _post(endpoint: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{_BASE}/{endpoint}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    response = urllib.request.urlopen(req, timeout=10)
    return json.loads(response.read())


def send_message(chat_id: str, text: str, parse_mode: str = "", reply_markup: Optional[dict] = None) -> int:
    payload: dict = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    result = _post("sendMessage", payload)
    return result["result"]["message_id"]


def send_long_message(chat_id: str, text: str, parse_mode: str = "") -> None:
    lines = text.split("\n")
    chunk = ""
    for line in lines:
        candidate = f"{chunk}\n{line}" if chunk else line
        if len(candidate) > _MAX_LENGTH:
            send_message(chat_id, chunk, parse_mode)
            chunk = line
        else:
            chunk = candidate
    if chunk:
        send_message(chat_id, chunk, parse_mode)


def edit_message(chat_id: str, message_id: int, text: str) -> None:
    try:
        _post("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})
    except Exception:
        pass


def get_updates(offset: int) -> list:
    result = _post("getUpdates", {"offset": offset, "timeout": 0})
    return result.get("result", [])


def get_me() -> dict:
    result = _post("getMe", {})
    return result.get("result", {})


def get_chat_administrators(chat_id: str) -> list:
    try:
        result = _post("getChatAdministrators", {"chat_id": chat_id})
        return result.get("result", [])
    except Exception:
        return []
