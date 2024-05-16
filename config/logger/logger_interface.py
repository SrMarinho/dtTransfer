from abc import ABC, abstractmethod

class ILogger(ABC):
    @abstractmethod
    def debug(self, msg: str):
        pass

    @abstractmethod
    def info(self, msg: str):
        pass

    @abstractmethod
    def warning(self, msg: str):
        pass

    @abstractmethod
    def error(self, msg: str):
        pass

    @abstractmethod
    def critical(self, msg: str):
        pass
