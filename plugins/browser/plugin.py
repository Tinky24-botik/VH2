from interfaces.plugin import Plugin
from interfaces.skill import Skill

from plugins.browser.skills.search import BrowserSearchSkill
from plugins.browser.skills.open_url import OpenUrlSkill
from plugins.browser.skills.open_site import OpenSiteSkill


class PluginImpl(Plugin):

    @property
    def plugin_id(self) -> str:
        return "browser"

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def get_skills(self) -> list[Skill]:
        return [
            BrowserSearchSkill(),
            OpenUrlSkill(),
            OpenSiteSkill(),
        ]