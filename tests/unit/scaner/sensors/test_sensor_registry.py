from typing import Generator

from tech_seeker.abstractions import AbstractFileContext
from tech_seeker.models import Dependency
from tech_seeker.scanner.sensors.base import BaseSensor, SensorRegistry


def test_register_sensor():
    class TestSensor(BaseSensor):
        def _scan(
            self, context: AbstractFileContext
        ) -> Generator[Dependency, None, None]:
            yield Dependency(
                name="test",
                version="0.0.1",
            )

    SensorRegistry.register_sensor(TestSensor)
    assert TestSensor in SensorRegistry._sensors


def test_duplicate_registration():
    old_sensors = SensorRegistry._sensors
    SensorRegistry._sensors = []

    class TestSensor(BaseSensor):
        def _scan(
            self, context: AbstractFileContext
        ) -> Generator[Dependency, None, None]:
            yield Dependency(
                name="test",
                version="0.0.1",
            )

    SensorRegistry.register_sensor(TestSensor)
    SensorRegistry.register_sensor(TestSensor)
    assert TestSensor in SensorRegistry._sensors
    assert len(SensorRegistry._sensors) == 1
    SensorRegistry._sensors = old_sensors


def test_sensors_generator():
    old_sensors = SensorRegistry._sensors
    SensorRegistry._sensors = []

    class TestSensor(BaseSensor):
        def _scan(
            self, context: AbstractFileContext
        ) -> Generator[Dependency, None, None]:
            yield Dependency(
                name="test",
                version="0.0.1",
            )

    SensorRegistry.register_sensor(TestSensor)
    sensors = list(SensorRegistry.sensors())
    assert len(sensors) == 1
    assert isinstance(sensors[0], TestSensor)

    SensorRegistry._sensors = old_sensors


def test_metaclass_registration():
    class TestSensor(BaseSensor):
        def _scan(
            self, context: AbstractFileContext
        ) -> Generator[Dependency, None, None]:
            yield Dependency(
                name="test",
                version="0.0.1",
            )

    assert TestSensor in SensorRegistry._sensors
