from unittest.mock import Mock

import pytest

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import Dependency
from tech_seeker.scanner.sensors import BaseSensor


@pytest.fixture
def mock_file_context():
    return Mock(spec=AbstractFileContext)


class TestSensor(BaseSensor):
    dependency_container_regex = ".*\\.txt$"

    def _scan(self, context):
        yield Dependency(name="test", version="1.0")


def test_is_dependency_container(mock_file_context):
    mock_file_context.path.return_value = "test.txt"
    sensor = TestSensor()
    assert sensor.is_dependency_container(mock_file_context)


def test_get_dependencies(mock_file_context):
    mock_file_context.path.return_value = "test.txt"
    sensor = TestSensor()
    dependencies = list(sensor.get_dependencies(mock_file_context))
    assert dependencies == [Dependency(name="test", version="1.0")]
