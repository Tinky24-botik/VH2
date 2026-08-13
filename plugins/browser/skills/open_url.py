import webbrowser
from urllib.parse import urlparse

from interfaces.skill import Skill


class OpenUrlSkill(Skill):

    @property
    def skill_id(self) -> str:
        return "browser.open_url"

    @property
    def name(self) -> str:
        return "Открытие URL"

    def execute(self, **kwargs):
        url = kwargs.get("url")

        if not url:
            return "Не указан адрес сайта"

        url = str(url).strip()

        if not url:
            return "Не указан адрес сайта"

        if not url.startswith(
            ("http://", "https://")
        ):
            url = "https://" + url

        parsed = urlparse(url)

        if not parsed.netloc:
            return f"Некорректный адрес: {url}"

        webbrowser.open(url)

        return f"Открываю {url}"