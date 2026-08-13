import json
import webbrowser
from urllib.parse import quote_plus

from interfaces.skill import Skill


class OpenSiteSkill(Skill):

    @property
    def skill_id(self) -> str:
        return "browser.open_site"

    @property
    def name(self) -> str:
        return "Открытие сайта"

    def execute(self, **kwargs):
        site = kwargs.get("site")

        if not site:
            return "Не указан сайт"

        site = str(site).strip().lower()

        if not site:
            return "Не указан сайт"

        sites = self._load_sites()

        if site in sites:
            url = sites[site]
            webbrowser.open(url)
            return f"Открываю {site}"

        if "." in site:
            url = site

            if not url.startswith(
                ("http://", "https://")
            ):
                url = "https://" + url

            webbrowser.open(url)
            return f"Открываю {url}"

        query = quote_plus(site)

        url = (
            "https://www.google.com/search?q="
            + query
        )

        webbrowser.open(url)

        return (
            f"Не знаю прямой адрес «{site}». "
            f"Ищу его в Google."
        )

    def _load_sites(self):
        with open(
            "config/settings.json",
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)
        return data.get("sites", {})