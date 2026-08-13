import webbrowser
from urllib.parse import quote_plus

from interfaces.skill import Skill


class BrowserSearchSkill(Skill):

    @property
    def skill_id(self) -> str:
        return "browser.search"

    @property
    def name(self) -> str:
        return "Поиск в браузере"

    def execute(self, **kwargs):
        query = kwargs.get("query")

        if not query:
            return "Не указан запрос для поиска"

        query = str(query).strip()

        if not query:
            return "Не указан запрос для поиска"

        url = (
            "https://www.google.com/search?q="
            + quote_plus(query)
        )

        webbrowser.open(url)

        return f"Ищу в браузере: {query}"