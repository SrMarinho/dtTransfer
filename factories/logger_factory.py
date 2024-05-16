
from config.logger.standard_logger import StandardLogger

class LoggerFactory:
    @staticmethod
    def getInstance(name:str = 'standardLogger'):
        loggers_list = {
                'standardLogger': StandardLogger
                }

        if name in loggers_list:
            return loggers_list[name]()
        else:
            raise ValueError("Unknown logger type")
