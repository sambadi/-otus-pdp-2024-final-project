from tech_seeker.scanner.sensors.base import BaseSensor, SensorRegistry


def test_register_sensor():
    class TestSensor(BaseSensor):
        pass

    SensorRegistry.register_sensor(TestSensor)
    assert TestSensor in SensorRegistry._sensors


def test_duplicate_registration():
    old_sensors = SensorRegistry._sensors
    SensorRegistry._sensors = []

    class TestSensor(BaseSensor):
        pass

    SensorRegistry.register_sensor(TestSensor)
    SensorRegistry.register_sensor(TestSensor)
    assert TestSensor in SensorRegistry._sensors
    assert len(SensorRegistry._sensors) == 1
    SensorRegistry._sensors = old_sensors


def test_sensors_generator():
    old_sensors = SensorRegistry._sensors
    SensorRegistry._sensors = []

    class TestSensor(BaseSensor):
        pass

    SensorRegistry.register_sensor(TestSensor)
    sensors = list(SensorRegistry.sensors())
    assert len(sensors) == 1
    assert isinstance(sensors[0], TestSensor)

    SensorRegistry._sensors = old_sensors


def test_metaclass_registration():
    class TestSensor(BaseSensor):
        pass

    assert TestSensor in SensorRegistry._sensors
