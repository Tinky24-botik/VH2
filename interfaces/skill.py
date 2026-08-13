from abc import ABC, abstractmethod


class Skill(ABC):

    @property
    @abstractmethod
    def skill_id(self) -> str:
        """
        Уникальный ID skill.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Человеческое название skill.
        """
        pass

    @abstractmethod
    def execute(self, **kwargs):
        """
        Выполнить skill.
        """
        pass