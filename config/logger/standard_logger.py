from config.logger.logger_interface import ILogger
import logging
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

class StandardLogger(ILogger):
    def __init__(self):
        self.logger = logging.getLogger('dtTransfer')
        
        log_level = logging.DEBUG if os.getenv("ENV_TYPE") == 'homolog' else logging.INFO
        self.logger.setLevel(log_level)

        log_filepath = self.create_log_directory()

        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(logging.DEBUG)
        streamFormatter = logging.Formatter('%(message)s')
        streamHandler.setFormatter(streamFormatter)

        self.logger.addHandler(streamHandler)

        fileHandler = logging.FileHandler(log_filepath, 'a')
        fileHandler.setLevel(logging.INFO)
        fileFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fileHandler.setFormatter(fileFormatter)

        self.logger.addHandler(fileHandler)

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
