import json
import os

from interfaces.skill import Skill
from core.fuzzy_match import find_match, NeedsConfirmation


class OpenProgramSkill(Skill):

    @property
    def skill_id(self) -> str:
        return "system.open_program"

    @property
    def name(self) -> str:
        return "Открытие программы"

    def execute(self, **kwargs):
        program_name = kwargs.get("name")
        confirmed = kwargs.get("confirmed", False)
        exclude = kwargs.get("exclude", set())

        if not program_name:
            return "Не указано имя программы"

        programs = self._load_programs()
        program_name_lower = program_name.lower()

        match = find_match(
            program_name_lower,
            programs,
            exclude=exclude,
        )

        if match.value is None:
            return (
                f"Не знаю программу «{program_name}», "
                f"добавь её в settings.json"
            )

        if match.needs_confirmation and not confirmed:
            return NeedsConfirmation(
                question=f"Ты имел в виду «{match.matched_key}»?",
                skill_id=self.skill_id,
                arguments={"name": program_name},
                guessed_key=match.matched_key,
            )

        os.startfile(match.value)

        if match.matched_key != program_name_lower:
            return (
                f"Открываю {match.matched_key} "
                f"(расслышал как «{program_name}»)"
            )

        return f"Открываю {match.matched_key}"

    def _load_programs(self):
        with open(
            "config/settings.json",
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)
        return data.get("programs", {})