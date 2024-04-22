from abc import ABC, abstractmethod

class Queryable(ABC):  # Classe abstrata Animal
    @staticmethod
    @abstractmethod
    def getQuery() -> str:
        ...

    @staticmethod
    @abstractmethod
    def transferConfig():
        ...
