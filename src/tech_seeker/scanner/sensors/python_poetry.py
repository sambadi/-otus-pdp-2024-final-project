from typing import Generator
import tomllib

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import UsageScope, Dependency
from tech_seeker.scanner.sensors.base import BaseSensor


class PythonPoetrySensor(BaseSensor):
    """
    Сенсор для извлечения зависимостей из файлов проектов python под управлением poetry
    """

    dependency_container_regex = r"(.+/)?poetry\.lock$"

    @staticmethod
    def __extract_dependencies(
        packages: dict[str, str] | None,
        locked_package_versions_map: dict[str, str],
        usage_scope: UsageScope,
    ) -> Generator[Dependency, None, None]:
        """Извлечение зависимостей из файлов проекта python под управлением poetry"""
        if packages is None:
            yield from []
        else:
            for dependency_name, _ in packages.items():
                dependency_name = dependency_name.lower()
                if dependency_name == "python":
                    yield Dependency(
                        type="python",
                        name=dependency_name,
                        version=_,
                        usage_scope=usage_scope,
                    )
                if version := locked_package_versions_map.get(dependency_name):
                    yield Dependency(
                        type="python",
                        name=dependency_name,
                        version=version,
                        usage_scope=usage_scope,
                    )

    def _scan(self, context: AbstractFileContext) -> Generator[Dependency, None, None]:
        """Извлечение зависимостей из файла проекта python под управлением poetry"""

        lock_data = tomllib.loads(context.content().decode())

        pyproject_path = context.path().replace("poetry.lock", "pyproject.toml")
        if not context.change_context(pyproject_path):
            return
        pyproject_data = tomllib.loads(context.content().decode())

        locked_package_versions_map = {
            package["name"]: package["version"]
            for package in lock_data.get("package", [])
        }

        poetry_setup = pyproject_data["tool"]["poetry"]
        yield from self.__extract_dependencies(
            packages=poetry_setup.get("dependencies"),
            locked_package_versions_map=locked_package_versions_map,
            usage_scope=UsageScope.RUNTIME,
        )
        yield from self.__extract_dependencies(
            packages=poetry_setup.get("group", {}).get("dev", {}).get("dependencies"),
            locked_package_versions_map=locked_package_versions_map,
            usage_scope=UsageScope.DEV,
        )
