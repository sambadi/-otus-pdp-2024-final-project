from pydantic import BaseModel, ConfigDict, Field

from tech_seeker.models.technology import UsageScope


class Dependency(BaseModel):
    """Описание зависимости"""

    model_config = ConfigDict(frozen=True)

    type: str = Field(
        default="Тип зависимости. "
        "Обозначает язык программирования для которого определяются зависимости",
        examples=["csharp", "go", "java", "javascript", "python"],
    )
    name: str = Field(
        description="Название зависимости, т.е. название технологии, определённой как зависимость в проекте"
    )
    version: str = Field(description="Версия технологии")
    usage_scope: UsageScope = Field(
        default=UsageScope.RUNTIME,
        description="Область использования зависимости в проекте",
        examples=[UsageScope.RUNTIME, UsageScope.DEV],
    )
