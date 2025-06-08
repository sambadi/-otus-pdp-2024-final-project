from unittest.mock import Mock, patch

import pytest

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import Dependency
from tech_seeker.scanner.sensors import BaseSensor


@pytest.fixture
def mock_file_context():
    return Mock(spec=AbstractFileContext)


@pytest.fixture
def mock_dependency_container_regex():
    with patch(
        "tech_seeker.scanner.sensors.base.BaseSensor.dependency_container_regex",
        ".*\\.txt$",
    ):
        yield


def test_is_dependency_container(mock_file_context, mock_dependency_container_regex):
    mock_file_context.path.return_value = "test.txt"
    sensor = BaseSensor()
    assert sensor.is_dependency_container(mock_file_context)


def test_get_dependencies(mock_file_context, mock_dependency_container_regex):
    class TestSensor(BaseSensor):
        def _scan(self, context):
            yield Dependency(name="test", version="1.0")

    mock_file_context.path.return_value = "test.txt"
    sensor = TestSensor()
    dependencies = list(sensor.get_dependencies(mock_file_context))
    assert dependencies == [Dependency(name="test", version="1.0")]
