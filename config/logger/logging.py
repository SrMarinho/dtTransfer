from factories.logger_factory import LoggerFactory

logger = LoggerFactory.getInstance()

def use(loggerName):
    logger = LoggerFactory.getInstance(loggerName)
