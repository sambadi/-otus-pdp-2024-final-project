from abc import ABC, abstractmethod
from typing import Self

from tech_seeker.abstractions.abstract_file_context import AbstractFileContext


class AbstractProjectContext(ABC):
    """
    Интерфейс контекста проекта.
    """

    @abstractmethod
    def name(self) -> str:
        """Возвращает имя контекста проекта"""

    def __iter__(self) -> Self:
        """Инициализация итератора"""
        return self

    @abstractmethod
    def __next__(self) -> AbstractFileContext:
        """
        Переход на следующий элемент в списке файлов
        """
