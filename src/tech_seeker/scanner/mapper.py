from importlib.abc import Traversable
from importlib.resources import files
from pathlib import Path

import yaml

from tech_seeker.abstractions import AbstractMapper
from tech_seeker.models import TechnologyMapping, Dependency, Technology


class Mapper(AbstractMapper):
    """Реализация маппера зависимостей проекта на технологии"""

    def __init__(self, group: str, prefix: str = ""):
        self._group = group
        self._skip: list[str] = []
        self._known: list[str] = []
        self._map: dict[str, list[TechnologyMapping]] = {}

    def _load_file(self, path: str | Traversable) -> "Mapper":
        """
        Загрузка настроек маппера из файла

        :param path: путь к файлу с настройками или экземпляр Traversable
        :return: Экземпляр класса Mapper
        """
        if isinstance(path, str):
            path = Path(path)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self._skip = data.get("skip", [])
        self._known = data.get("known", [])
        self._map = {
            k: [TechnologyMapping(**mapping) for mapping in v]
            for k, v in data.get("map", {}).items()
        }

        return self

    @classmethod
    def from_file(cls, path: str | Traversable, group: str) -> "Mapper":
        """
        Инициализация маппера из файла

        :param path: путь к файлу маппера
        :param group: группа зависимостей
        :return: маппер
        """
        return cls(group)._load_file(path)

    def map(self, dep: Dependency) -> set[Technology]:
        if dep.name.lower() in self._skip:
            return set()
        if mapping := self._map.get(dep.name):
            return {
                Technology(
                    group=self._group,
                    name=m.to,
                    version=dep.version if m.keep_version else None,
                    is_known=True,
                    usage_scope=dep.usage_scope,
                )
                for m in mapping
            }
        is_known: bool = True if dep.name in self._known else False
        return {
            Technology(
                group=self._group,
                name=dep.name.lower(),
                version=dep.version,
                is_known=is_known,
                usage_scope=dep.usage_scope,
            )
        }


def get_default_mappers() -> dict[str, Mapper]:
    """Возвращает словарь с дефолтными мапперами"""
    return {
        file.name[:-5]: Mapper.from_file(file, file.name[:-5])
        for file in files("tech_seeker").joinpath("mappings").iterdir()
    }
