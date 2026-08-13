from dataclasses import dataclass

from core.skill_registry import SkillRegistry


@dataclass
class Command:
    """
    Нормализованная команда для выполнения.
    """

    skill_id: str
    arguments: dict


class CommandRouter:

    def __init__(self, skill_registry: SkillRegistry):
        self.skill_registry = skill_registry

    def route(self, command: Command):
        """
        Находит Skill и передаёт ему аргументы.
        """

        skill = self.skill_registry.get(
            command.skill_id
        )

        if skill is None:
            return (
                f"Неизвестная команда: "
                f"{command.skill_id}"
            )

        try:
            return skill.execute(
                **command.arguments
            )

        except Exception as error:
            return (
                f"Ошибка выполнения "
                f"{command.skill_id}: {error}"
            )