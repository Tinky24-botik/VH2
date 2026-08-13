from interfaces.skill import Skill


class SkillRegistry:

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """
        Регистрирует skill по уникальному ID.
        """

        if skill.skill_id in self._skills:
            raise ValueError(
                f"Skill с ID '{skill.skill_id}' уже зарегистрирован"
            )

        self._skills[skill.skill_id] = skill

    def unregister(self, skill_id: str) -> bool:
        """
        Удаляет skill из Registry.

        Возвращает True, если skill существовал.
        """

        if skill_id not in self._skills:
            return False

        del self._skills[skill_id]
        return True

    def get(self, skill_id: str) -> Skill | None:
        """
        Возвращает skill по ID.
        """

        return self._skills.get(skill_id)

    def get_all(self) -> list[Skill]:
        """
        Возвращает список всех зарегистрированных skills.
        """

        return list(self._skills.values())

    def has(self, skill_id: str) -> bool:
        """
        Проверяет наличие skill.
        """

        return skill_id in self._skills

    def clear(self) -> None:
        """
        Полностью очищает Registry.
        """

        self._skills.clear()