from unittest.mock import patch

from tech_seeker.models import Dependency, Technology, TechnologyMapping, UsageScope
from tech_seeker.scanner.mapper import Mapper


def test_mapper_skip():
    """
    Проверка игнорирования зависимостей маппером
    """
    mapper = Mapper("test")

    with patch.object(mapper, "_skip", ["dependency_name"]):
        techs = mapper.map(
            Dependency(type="test", name="Dependency_Name", version="1.0.0")
        )
        assert len(techs) == 0


def test_mapper_map_known_dependency():
    """
    Проверка маппинга известных зависимостей на технологии
    """
    mapper = Mapper("test")

    dependency_map = {
        "Dependency_Name": [
            TechnologyMapping(to="sqlserver", keep_version=False),
            TechnologyMapping(to="dependency", keep_version=True),
        ]
    }

    with patch.object(mapper, "_map", dependency_map):
        techs = mapper.map(
            Dependency(type="test", name="Dependency_Name", version="1.0.0"),
        )

        assert techs == {
            Technology(
                group="test",
                name="sqlserver",
                version=None,
                is_known=True,
                usage_scope=UsageScope.RUNTIME,
            ),
            Technology(
                group="test",
                name="dependency",
                version="1.0.0",
                is_known=True,
                usage_scope=UsageScope.RUNTIME,
            ),
        }


def test_mapper_map_unknown_dependency():
    """Тестирование маппинга неизвестной зависимости на технологии"""

    mapper = Mapper("test")

    techs = mapper.map(
        Dependency(type="test", name="UnknownDependency", version="1.0.0"),
    )

    assert techs == {
        Technology(
            group="test",
            name="unknowndependency",
            version="1.0.0",
            is_known=False,
            usage_scope=UsageScope.RUNTIME,
        )
    }
