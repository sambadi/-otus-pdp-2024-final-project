from typing import Mapping

from tech_seeker.abstractions import AbstractProjectContext, AbstractMapper
from tech_seeker.models import Technology, Dependency
from tech_seeker.scanner.mapper import get_default_mappers
from tech_seeker.scanner.sensors import SensorRegistry


class UnknownMapperError(Exception):
    pass


class Scaner:
    """Сканер зависимостей"""

    def __init__(
        self,
        mappers: Mapping[str, AbstractMapper] | None = None,
    ) -> None:
        self._mappers: Mapping[str, AbstractMapper] = mappers or get_default_mappers()

    def _map_dependency_to_technologies(
        self, techs: set[Technology], dependency: Dependency
    ) -> None:
        if mapper := self._mappers.get(dependency.type):
            for tech in mapper.map(dependency):
                techs.add(tech)
        else:
            raise UnknownMapperError(
                f"Mapper for dependency type {dependency.type} not registered"
            )

    def scan(self, context: AbstractProjectContext) -> set[Technology]:
        techs: set[Technology] = set()

        for file in context:
            for sensor in SensorRegistry.sensors():
                for dependency in sensor.get_dependencies(file):
                    self._map_dependency_to_technologies(techs, dependency)

        return techs
