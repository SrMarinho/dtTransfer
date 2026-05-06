import logging
import threading
import json
import urllib.request
from datetime import datetime
from typing import Optional


_MAX_LENGTH = 4096


def send_telegram(token: str, chat_id: str, text: str, parse_mode: str = "") -> None:
    lines = text.split("\n")
    chunk = ""
    for line in lines:
        candidate = f"{chunk}\n{line}" if chunk else line
        if len(candidate) > _MAX_LENGTH:
            _send_chunk(token, chat_id, chunk, parse_mode)
            chunk = line
        else:
            chunk = candidate
    if chunk:
        _send_chunk(token, chat_id, chunk, parse_mode)


def _send_chunk(token: str, chat_id: str, text: str, parse_mode: str = "") -> None:
    payload: dict = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=10)


class TelegramHandler(logging.Handler):
    """
    Agrupa erros recebidos dentro de `batch_window` segundos e envia
    um único mensagem ao Telegram em background — não bloqueia o logger.
    """

    def __init__(self, token: str, chat_id: str, batch_window: float = 10.0):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.batch_window = batch_window
        self._pending: list[str] = []
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None

    def emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            self._pending.append(self.format(record))
            if self._timer is None:
                self._timer = threading.Timer(self.batch_window, self._flush)
                self._timer.daemon = True
                self._timer.start()

    def _flush(self) -> None:
        with self._lock:
            messages = self._pending[:]
            self._pending.clear()
            self._timer = None
        if messages:
            threading.Thread(target=self._send_batch, args=(messages,), daemon=True).start()

    def _send_batch(self, messages: list[str]) -> None:
        count = len(messages)
        header = f"❌ dataReplicator — {count} erro(s) em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        body = "\n".join(f"• {m}" for m in messages)
        try:
            send_telegram(self.token, self.chat_id, f"{header}\n\n{body}")
        except Exception:
            pass

    def close(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            messages = self._pending[:]
            self._pending.clear()
        if messages:
            self._send_batch(messages)
        super().close()
