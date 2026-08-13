from interfaces.plugin import Plugin
from interfaces.skill import Skill
from plugins.youtube.skills.search import YoutubeSearchSkill


class PluginImpl(Plugin):

    @property
    def plugin_id(self) -> str:
        return "youtube"

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_skills(self) -> list[Skill]:
        return [
            YoutubeSearchSkill()
        ]
    