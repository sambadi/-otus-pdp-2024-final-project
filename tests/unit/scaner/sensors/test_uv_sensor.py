from unittest.mock import patch, MagicMock, Mock
from tech_seeker.scanner.sensors.python_uv import PythonUvSensor
from tech_seeker.models import UsageScope
from tech_seeker.abstractions import AbstractFileContext


def test_scan_python_version():
    sensor = PythonUvSensor()
    context = MagicMock(spec=AbstractFileContext)
    context.path.return_value = "uv.lock"
    context.change_context.return_value = True
    context.content.return_value = b"3.9\n"

    with patch.object(PythonUvSensor, "_get_python_version", return_value="3.9"):
        with patch.object(
            PythonUvSensor, "_extract_locked_package_versions_map", return_value={}
        ):
            with patch.object(
                PythonUvSensor, "_get_pyproject_content", return_value=None
            ):
                result = list(sensor._scan(context))
                assert result[0].name == "python"
                assert result[0].version == "3.9"
                assert result[0].usage_scope == UsageScope.RUNTIME


def test_scan_dependencies():
    mock_lock_data = b"""
    [[package]]
    name = "requests"
    version = "2.25.1"
    [[package]]
    name = "flask"
    version = "2.0.1"
    [[package]]
    name = "pytest"
    version = "8.4.0"
    """
    mock_pyproject_data = b"""
    [project]
    requires-python = ">=3.12"
    dependencies = [
        "requests>=2.31.0",
        "flask>=2.1.2",
    ]   
        
    [dependency-groups]
    dev = [
        "pytest>=8.4.0"
    ]
    """

    mock_context = Mock(spec=AbstractFileContext)
    mock_context.path.return_value = "uv.lock"
    mock_context.content = Mock(side_effect=[mock_lock_data, mock_pyproject_data])
    mock_context.change_context.return_value = True

    with patch.object(PythonUvSensor, "_get_python_version", return_value="3.9"):
        sensor = PythonUvSensor()
        result = list(sensor._scan(mock_context))

        assert len(result) == 4
        assert result[0].name == "python"
        assert result[0].version == "3.9"
        assert result[0].usage_scope == UsageScope.RUNTIME

        assert result[1].name == "requests"
        assert result[1].version == "2.25.1"
        assert result[1].usage_scope == UsageScope.RUNTIME

        assert result[2].name == "flask"
        assert result[2].version == "2.0.1"
        assert result[2].usage_scope == UsageScope.RUNTIME

        assert result[3].name == "pytest"
        assert result[3].version == "8.4.0"
        assert result[3].usage_scope == UsageScope.DEV
