from abc import ABC, abstractmethod


class AbstractFileContext(ABC):
    """
    Интерфейс контекста обхода файла.
    """

    @abstractmethod
    def change_context(self, path: str) -> bool:
        """Изменение пути к файлу"""

    @abstractmethod
    def path(self) -> str:
        """Путь к файлу"""

    @abstractmethod
    def content(self) -> bytes:
        """Содержимое файла"""
