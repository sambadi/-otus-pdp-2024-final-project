import os
import re
from typing import Generator
import tomllib

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import UsageScope, Dependency
from tech_seeker.scanner.sensors.base import BaseSensor


class PythonRyeSensor(BaseSensor):
    """
    Сенсор для извлечения зависимостей из файлов проектов python под управлением Rye
    """

    dependency_container_regex = r"(.+/)?requirements(-dev)?\.lock$"
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
        pyproject_path: str = original_context_path.replace(
            os.path.basename(original_context_path), "pyproject.toml"
        )
        if not context.change_context(pyproject_path):
            return None

        pyproject_data = tomllib.loads(context.content().decode(encoding="utf-8"))
        context.change_context(original_context_path)

        if not pyproject_data.get("tool", {}).get("rye", {}).get("managed"):
            # Если проект не под управлением rye, то возвращаем None
            return None

        return pyproject_data

    @staticmethod
    def _extract_locked_package_versions_map(context: AbstractFileContext) -> dict:
        """Извлечение зафиксированных версий зависимостей из requirements[-dev].lock"""
        package_name_and_version_regex = re.compile(r"^(\w[^>~=]*)\s*[=]{2}([\d.]+).*$")
        lock_data = context.content().decode(encoding="utf-8")
        locked_package_versions_map = {}
        for row in lock_data.splitlines():
            row = row.strip()
            if match := package_name_and_version_regex.match(row):
                locked_package_versions_map[match.group(1)] = match.group(2)

        return locked_package_versions_map

    @staticmethod
    def _get_python_version(context: AbstractFileContext) -> str | None:
        """Извлечение версии Python"""
        original_context_path: str = context.path()
        version_file_path: str = original_context_path.replace(
            os.path.basename(original_context_path), ".python-version"
        )
        if not context.change_context(version_file_path):
            return None

        version = context.content().decode(encoding="utf-8")
        context.change_context(original_context_path)
        return version.strip("\n")

    def _scan(self, context: AbstractFileContext) -> Generator[Dependency, None, None]:
        """Извлечение зависимостей из файла проекта python под управлением rye"""
        locked_package_versions_map = self._extract_locked_package_versions_map(context)

        pyproject_content = self._get_pyproject_content(context)

        if not pyproject_content:
            return

        if context.path().endswith("-dev.lock"):
            yield from self.__extract_dependencies(
                packages=pyproject_content.get("tool", {})
                .get("rye", {})
                .get("dev-dependencies", []),
                locked_package_versions_map=locked_package_versions_map,
                usage_scope=UsageScope.DEV,
            )
        else:
            python_version = self._get_python_version(context)
            if python_version:
                yield Dependency(
                    type="python",
                    name="python",
                    version=python_version,
                    usage_scope=UsageScope.RUNTIME,
                )
            yield from self.__extract_dependencies(
                packages=pyproject_content["project"]["dependencies"],
                locked_package_versions_map=locked_package_versions_map,
                usage_scope=UsageScope.RUNTIME,
            )
