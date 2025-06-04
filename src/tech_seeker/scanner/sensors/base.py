import re
from abc import abstractmethod
from typing import Generator, Type

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import Dependency


class SensorRegistry:
    """Реестр сенсоров"""

    _sensors: list[Type["BaseSensor"]] = []

    @classmethod
    def register_sensor(cls, sensor: Type["BaseSensor"]):
        if sensor in cls._sensors:
            return
        cls._sensors.append(sensor)

    @classmethod
    def sensors(cls) -> Generator["BaseSensor", None, None]:
        for sensor_type in cls._sensors:
            yield sensor_type()


class SensorMeta(type):
    """Метакласс для автоматической регистрации сенсоров в SensorRegistry"""

    def __new__(cls, *args, **kwargs):
        cls_ = super().__new__(cls, *args, **kwargs)
        if cls_.__name__ != "BaseSensor":
            SensorRegistry.register_sensor(cls_)
        return cls_


class BaseSensor(metaclass=SensorMeta):
    """
    Интерфейс сенсора
    """

    dependency_container_regex = ""
    """Регулярное выражение для определения поддерживаемых сенсором файлов"""

    def __init__(self) -> None:
        self._regex = re.compile(self.dependency_container_regex)

    def is_dependency_container(self, file_context: AbstractFileContext) -> bool:
        return self._regex.match(file_context.path()) is not None

    def get_dependencies(
        self, context: AbstractFileContext
    ) -> Generator[Dependency, None, None]:
        """
        Запуск сенсора на текущем контексте

        :param context: Контекст сканируемого файла
        """

        if not self.is_dependency_container(context):
            return

        yield from self._scan(context)

    @abstractmethod
    def _scan(self, context: AbstractFileContext) -> Generator[Dependency, None, None]:
        """Запуск сканирования зависимостей сенсором на текущем контексте"""
