import re
from typing import Generator
import tomllib

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import UsageScope, Dependency
from tech_seeker.scanner.sensors.base import BaseSensor


class PythonUvSensor(BaseSensor):
    """
    Сенсор для извлечения зависимостей из файлов проектов python под управлением uv
    """

    dependency_container_regex = r"(.+/)?uv\.lock$"
    dependency_name_regex = r"^([^\[>=~\s;]*).*$"

    def __init__(self):
        super().__init__()
        self._dep_name_regex = re.compile(self.dependency_name_regex)

    @staticmethod
    def _package_name_to_dependency(
        package_name: str,
        locked_package_versions_map: dict[str, str],
        usage_scope: UsageScope,
    ) -> Generator[Dependency, None, None]:
        if version := locked_package_versions_map.get(package_name):
            yield Dependency(
                type="python",
                name=package_name.lower(),
                version=version,
                usage_scope=usage_scope,
            )

    def _extract_package_name(self, pkg: str) -> str:
        """Извлечение имени пакета из строки"""
        return self._dep_name_regex.match(pkg).group(1)

    def __extract_dependencies(
        self,
        packages: list[str] | None,
        locked_package_versions_map: dict[str, str],
        usage_scope: UsageScope,
    ) -> Generator[Dependency, None, None]:
        """Извлечение зависимостей из списка строк"""
        if not packages:
            return

        for package_name in packages:
            package_name = self._extract_package_name(package_name.lower())
            if version := locked_package_versions_map.get(package_name):
                yield Dependency(
                    type="python",
                    name=package_name,
                    version=version,
                    usage_scope=usage_scope,
                )

    @staticmethod
    def _get_pyproject_content(context: AbstractFileContext) -> dict | None:
        """Извлечение содержимого pyproject.toml"""
        original_context_path: str = context.path()
        pyproject_path: str = original_context_path.replace("uv.lock", "pyproject.toml")
        if not context.change_context(pyproject_path):
            return None
        pyproject_data = tomllib.loads(context.content().decode(encoding="utf-8"))
        context.change_context(original_context_path)
        return pyproject_data

    @staticmethod
    def _extract_locked_package_versions_map(context: AbstractFileContext) -> dict:
        """Извлечение зафиксированных версий зависимостей из uv.lock"""
        lock_data = tomllib.loads(context.content().decode(encoding="utf-8"))
        locked_package_versions_map = {
            package["name"]: package["version"]
            for package in lock_data.get("package", [])
        }
        return locked_package_versions_map

    @staticmethod
    def _get_python_version(context: AbstractFileContext) -> str | None:
        """Извлечение версии Python"""
        original_context_path: str = context.path()
        version_file_path: str = original_context_path.replace(
            "uv.lock", ".python-version"
        )
        if not context.change_context(version_file_path):
            return None

        version = context.content().decode(encoding="utf-8")

        context.change_context(original_context_path)
        return version.strip("\n")

    def _scan(self, context: AbstractFileContext) -> Generator[Dependency, None, None]:
        """Извлечение зависимостей из файла проекта python под управлением uv"""
        python_version = self._get_python_version(context)
        if python_version:
            yield Dependency(
                type="python",
                name="python",
                version=python_version,
                usage_scope=UsageScope.RUNTIME,
            )

        locked_package_versions_map = self._extract_locked_package_versions_map(context)

        pyproject_content = self._get_pyproject_content(context)

        if not pyproject_content:
            return

        yield from self.__extract_dependencies(
            packages=pyproject_content["project"]["dependencies"],
            locked_package_versions_map=locked_package_versions_map,
            usage_scope=UsageScope.RUNTIME,
        )

        yield from self.__extract_dependencies(
            packages=pyproject_content.get("dependency-groups", {}).get("dev", []),
            locked_package_versions_map=locked_package_versions_map,
            usage_scope=UsageScope.DEV,
        )
