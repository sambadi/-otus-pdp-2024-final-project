from unittest.mock import Mock

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import UsageScope
from tech_seeker.scanner.sensors.python_poetry import PythonPoetrySensor


def test_extract_dependencies():
    mock_lock_data = b"""
    [[package]]
    name = "requests"
    version = "2.31.0"
    [[package]]
    name = "pytest"
    version = "6.2.4"
    """
    mock_pyproject_data = b"""
    [tool.poetry.dependencies]
    python = ">=3.9.0,<3.13"
    requests = "2.31.0"
    
    [tool.poetry.group.dev.dependencies]
    pytest = "6.2.4"
    """

    mock_context = Mock(spec=AbstractFileContext)
    mock_context.content = Mock(side_effect=[mock_lock_data, mock_pyproject_data])
    mock_context.change_context.return_value = True

    sensor = PythonPoetrySensor()
    dependencies = list(sensor._scan(mock_context))

    assert len(dependencies) == 3
    python_dep = dependencies[0]
    assert python_dep.name == "python"
    assert python_dep.version == ">=3.9.0,<3.13"
    assert python_dep.usage_scope == UsageScope.RUNTIME

    requests_dep = dependencies[1]
    assert requests_dep.name == "requests"
    assert requests_dep.version == "2.31.0"
    assert requests_dep.usage_scope == UsageScope.RUNTIME
    pytest_dep = dependencies[2]
    assert pytest_dep.name == "pytest"
    assert pytest_dep.version == "6.2.4"
    assert pytest_dep.usage_scope == UsageScope.DEV
