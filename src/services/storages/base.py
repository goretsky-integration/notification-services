import pathlib
import sqlite3
from typing import Self
from abc import ABC, abstractmethod

__all__ = ('Storage',)


class Storage(ABC):

    def __init__(self, storage_file_path: str | pathlib.Path) -> None:
        self.__storage_file_path = storage_file_path
        self._connection = sqlite3.connect(self.__storage_file_path)
        self.init_tables()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    @abstractmethod
    def init_tables(self) -> None:
        pass
