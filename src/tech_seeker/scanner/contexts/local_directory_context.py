import os
from pathlib import Path
from typing import Self, Any

from tech_seeker.abstractions import AbstractProjectContext, AbstractFileContext


class LocalFileContext(AbstractFileContext):
    """Контекст для работы с файлами в локальной директории"""

    def __init__(self, file_path: str):
        super().__init__()
        self._file_path = file_path

    def change_context(self, path: str) -> bool:
        """Сменить текущий файловый контекст"""
        if os.path.exists(path):
            self._file_path = path
            return True

        return False

    def path(self) -> str:
        """Получить путь к текущему файлу"""
        return self._file_path

    def content(self) -> bytes:
        """Получить содержимое текущего файла"""
        with open(self._file_path, "rb") as file:
            return file.read()


class LocalDirectoryContext(AbstractProjectContext):
    """Контекст для работы с файлами в локальной директории"""

    def __init__(self, directory_path: str):
        super().__init__()

        self._directory = Path(directory_path)
        self._glob_iterator: Any = None

    def name(self) -> str:
        """Имя контекста"""
        return self._directory.name

    def __iter__(self) -> Self:
        """Инициализация итератора"""
        self._glob_iterator = self._directory.rglob("*")
        return self

    def __next__(self) -> AbstractFileContext:
        """Получение следующего файла из итератора"""
        while True:
            path: Path = next(self._glob_iterator)
            if not path:
                raise StopIteration()
            if path.is_dir():
                continue
            return LocalFileContext(file_path=path.as_posix())

        raise StopIteration()
