from interfaces.plugin import Plugin
from interfaces.skill import Skill
from plugins.telegram.skills.send_message import TelegramSendMessageSkill


class PluginImpl(Plugin):

    @property
    def plugin_id(self) -> str:
        return "telegram"

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_skills(self) -> list[Skill]:
        return [
            TelegramSendMessageSkill()
        ]