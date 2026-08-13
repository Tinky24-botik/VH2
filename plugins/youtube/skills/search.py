import os
import difflib
import webbrowser
import requests
from dotenv import load_dotenv

from interfaces.skill import Skill
from core.fuzzy_match import NeedsSelection

load_dotenv()

MAX_RESULTS = 5
TITLE_MATCH_CUTOFF = 0.75


class YoutubeSearchSkill(Skill):

    @property
    def skill_id(self) -> str:
        return "youtube.search"

    @property
    def name(self) -> str:
        return "Поиск на YouTube"

    def execute(self, **kwargs):
        selected_index = kwargs.get("selected_index")
        video_map = kwargs.get("video_map")

        if selected_index is not None:
            return self._open_from_map(selected_index, video_map or {})

        query = kwargs.get("query")

        if not query:
            return "Не указан запрос для поиска"

        api_key = os.getenv("YOUTUBE_API_KEY")

        if not api_key:
            return "Не найден YOUTUBE_API_KEY, проверь .env"

        items = self._search(query, api_key)

        if not items:
            return f"Ничего не нашёл по запросу «{query}»"

        titles = [item["snippet"]["title"] for item in items]

        close = difflib.get_close_matches(
            query,
            titles,
            n=1,
            cutoff=TITLE_MATCH_CUTOFF,
        )

        if close:
            index = titles.index(close[0])
            return self._open_video(items[index])

        video_map = {
            str(i + 1): {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
            }
            for i, item in enumerate(items)
        }

        options_text = "\n".join(
            f"{i + 1}. {title}"
            for i, title in enumerate(titles)
        )

        return NeedsSelection(
            question=f"Нашёл несколько вариантов:\n{options_text}",
            options=titles,
            skill_id=self.skill_id,
            arguments={},
            video_map=video_map,
        )

    def _search(self, query: str, api_key: str) -> list:
        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": MAX_RESULTS,
                "key": api_key,
            },
            timeout=10,
        )
        data = response.json()
        return data.get("items", [])

    def _open_video(self, item: dict) -> str:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        webbrowser.open(url)
        return f"Открываю: {title}"

    def _open_from_map(self, selected_index, video_map: dict) -> str:
        entry = video_map.get(str(selected_index))

        if not entry:
            return "Не понял, какой вариант выбрать"

        url = f"https://www.youtube.com/watch?v={entry['video_id']}"
        webbrowser.open(url)
        return f"Открываю: {entry['title']}"