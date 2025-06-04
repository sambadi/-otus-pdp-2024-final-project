from pydantic import BaseModel, ConfigDict, Field


class TechnologyMapping(BaseModel):
    """Описание маппинга технологии"""

    model_config = ConfigDict(frozen=True)

    to: str = Field(
        description="Название технологии из таблицы технологий организации, "
        "на которую мапится рассматриваемая зависимость"
    )
    keep_version: bool = Field(
        default=True,
        description="Флаг, определяющий нужно ли использовать определённую версию зависимости "
        "в качестве версии технологии, на которую осуществляется маппинг",
    )
