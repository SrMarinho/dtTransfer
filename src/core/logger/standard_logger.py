from src.core.logger.logger_interface import ILogger
from src.core.logger.telegram_handler import TelegramHandler
from src.core.logger.run_context import get_run_hash
import logging
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


class _RunHashFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        h = get_run_hash()
        record.run_hash = f'[{h}] ' if h else ''
        return True


class StandardLogger(ILogger):
    def __init__(self):
        self.logger = logging.getLogger('DataReplicator')

        self.logger.setLevel(
            getattr(
                logging,
                os.getenv("LOG_LEVEL", "INFO").upper()
            )
        )

        log_filepath = self.create_log_directory()
        run_hash_filter = _RunHashFilter()

        class SingleLineFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                message = super().format(record)
                return message.replace('\n', ' ').replace('\r', ' ')

        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logging.DEBUG)
        streamHandler.addFilter(run_hash_filter)
        streamHandler.setFormatter(SingleLineFormatter('%(run_hash)s%(message)s'))

        self.logger.addHandler(streamHandler)

        fileHandler = logging.FileHandler(log_filepath, 'a', encoding='utf-8')
        fileHandler.setLevel(logging.INFO)
        fileHandler.addFilter(run_hash_filter)
        fileHandler.setFormatter(SingleLineFormatter('%(asctime)s - %(levelname)s - %(run_hash)s%(message)s'))

        self.logger.addHandler(fileHandler)

        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if telegram_token and telegram_chat_id:
            telegramHandler = TelegramHandler(token=telegram_token, chat_id=telegram_chat_id)
            telegramHandler.setLevel(logging.ERROR)
            telegramHandler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(telegramHandler)

    def create_log_directory(self):
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%d')

        log_directory = os.path.join('logs', year, month)
        os.makedirs(log_directory, exist_ok=True)

        log_filename = f'{year}{month}{day}.log'
        log_filepath = os.path.join(log_directory, log_filename)

        return log_filepath

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)
