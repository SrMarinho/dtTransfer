from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def connection():
        raise NotImplementedError()

    @abstractmethod
    def getCursor():
        raise NotImplementedError()