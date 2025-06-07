from unittest.mock import MagicMock, patch

import pytest
from unittest import mock
from tech_seeker.scanner.scaner import Scaner, UnknownMapperError
from tech_seeker.models import Technology, Dependency
from tech_seeker.abstractions import AbstractProjectContext, AbstractMapper


def test_scan_maps_dependencies_successfully():
    """Тестируем нормальный сценарий работы сканера"""
    # Mock AbstractProjectContext
    context_mock = MagicMock(spec=AbstractProjectContext)
    context_mock.__iter__.return_value = [mock.MagicMock()]

    # Mock SensorRegistry.sensors()
    sensors = [mock.MagicMock()]
    with patch('tech_seeker.scanner.scaner.SensorRegistry.sensors', return_value=sensors):

        # Mock sensor's get_dependencies
        sensors[0].get_dependencies.return_value = [mock.MagicMock(spec=Dependency, type='some_type')]

        # Mock mapper for 'some_type'
        mapper = mock.MagicMock(spec=AbstractMapper)
        mapper.map.return_value = [mock.MagicMock(spec=Technology)]

        # Setup Scaner with custom mappers
        scaner = Scaner(mappers={'some_type': mapper})

        # Call scan
        result = scaner.scan(context_mock)

        # Assertions
        assert len(result) == 1
        mapper.map.assert_called_once_with(sensors[0].get_dependencies.return_value[0])


def test_scan_raises_unknown_mapper_error():
    """Тестируем работу Scaner при несуществующем mapper, должно быть выброшено исключение"""
    # Mock AbstractProjectContext
    context_mock = MagicMock(spec=AbstractProjectContext)
    context_mock.__iter__.return_value = [mock.MagicMock()]

    # Mock SensorRegistry.sensors()
    sensors = [mock.MagicMock()]
    with patch('tech_seeker.scanner.scaner.SensorRegistry.sensors', return_value=sensors):
            # Mock sensor's get_dependencies
        sensors[0].get_dependencies.return_value = [mock.MagicMock(spec=Dependency, type='unknown_type')]

        # Create Scaner with no mappers (uses default)
        scaner = Scaner()

        # Check for exception
        with pytest.raises(UnknownMapperError):
            scaner.scan(context_mock)


def test_scan_returns_empty_set_when_no_dependencies():
    """Тестируем работу сканера в случае когда список зависимостей пуст"""
    # Mock AbstractProjectContext
    context_mock = MagicMock(spec=AbstractProjectContext)
    context_mock.__iter__.return_value = [mock.MagicMock()]

    # Mock SensorRegistry.sensors()
    sensors = [mock.MagicMock()]
    with patch('tech_seeker.scanner.scaner.SensorRegistry.sensors', return_value=sensors):

        # Mock sensor's get_dependencies to return nothing
        sensors[0].get_dependencies.return_value = []

        # Create Scaner with default mappers
        scaner = Scaner()

        # Call scan
        result = scaner.scan(context_mock)

        # Assertions
        assert len(result) == 0