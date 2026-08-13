from interfaces.plugin import Plugin
from interfaces.skill import Skill

from plugins.system.skills.open_program import (
    OpenProgramSkill
)

from plugins.system.skills.close_program import (
    CloseProgramSkill
)


class PluginImpl(Plugin):

    @property
    def plugin_id(self) -> str:
        return "system"

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_skills(self) -> list[Skill]:
        return [
            OpenProgramSkill(),
            CloseProgramSkill(),
        ]