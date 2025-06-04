from abc import ABC, abstractmethod

from tech_seeker.models import Dependency, Technology


class AbstractMapper(ABC):
    """
    Интерфейс маппера зависимостей на набор технологий
    """

    @abstractmethod
    def map(self, dep: Dependency) -> set[Technology]:
        """
        Маппинг зависимости проекта на набор технологий, к которым она относится

        :param dep: зависимость
        :return: набор технологий
        """
