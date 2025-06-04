from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class UsageScope(StrEnum):
    """
    Область использования технологии в проектах
    """

    RUNTIME = "Runtime"  # Используется при запуске проекта
    DEV = "Dev"  # Используется при разработке, не используется при запуске проекта


class Technology(BaseModel):
    """Описание технологии"""

    model_config = ConfigDict(frozen=True)

    group: str = Field(
        default="Группа технологий. "
        "Обозначает язык программирования для которого определяются зависимости",
        examples=["csharp", "go", "java", "javascript", "python"],
    )
    name: str = Field(description="Название технологии")
    version: str | None = Field(default=None, description="Версия технологии")
    is_known: bool = Field(
        default=True,
        description="Флаг, отображающий определена ли данная технология, "
        "в качестве известной (определённой в таблице технологий организации) технологии "
        "в файле маппинга зависимостей на технологии",
    )
    usage_scope: UsageScope = Field(
        default=UsageScope.RUNTIME,
        description="Область использования технологии в проекте",
        examples=[UsageScope.RUNTIME, UsageScope.DEV],
    )
