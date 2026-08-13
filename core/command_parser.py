import re
import difflib

from core.router import Command


class CommandParser:

    OPEN_WORDS = {
        "открой",
        "запусти",
        "запустить",
        "открыть",
    }

    CLOSE_WORDS = {
        "закрой",
        "закрыть",
        "выключи",
    }

    SEARCH_WORDS = {
        "найди",
        "найти",
        "поищи",
        "поиск",
    }

    SEND_WORDS = {
        "напиши",
        "отправь",
    }

    VIDEO_WORDS = {
        "видео",
        "ролик",
        "ролики",
    }

    YOUTUBE_WORDS = {
        "ютуб",
        "youtube",
    }

    MATCH_CUTOFF = 0.7

    # ==================================================
    # MAIN PARSER
    # ==================================================

    def parse(self, text: str) -> Command | None:
        if text is None:
            return None

        text = str(text).lower().strip()

        if not text:
            return None

        words = re.split(r"\s+", text)

        if not words:
            return None

        action = words[0]
        rest_words = words[1:]

        if (
            rest_words
            and rest_words[0] in {"сообщение", "смс"}
        ):
            rest_words = rest_words[1:]

        rest = " ".join(rest_words).strip()

        matched = self._match_action(action)

        if matched is None:
            return None

        category, _ = matched

        # ==================================================
        # SEARCH
        # ==================================================

        if category == "search":
            return self._parse_search(rest_words)

        # ==================================================
        # OPEN
        # ==================================================

        if category == "open":

            if not rest_words:
                return None

            # ----------------------------------------------
            # "открой видео ..."
            # ----------------------------------------------

            if self._contains_video_words(rest_words):
                query_words = self._remove_video_markers(rest_words)
                query_words = self._remove_youtube_markers(query_words)
                query = " ".join(query_words).strip()

                if not query:
                    return None

                return Command(
                    skill_id="youtube.search",
                    arguments={"query": query}
                )

            # ----------------------------------------------
            # "открой на ютубе ..."
            # ----------------------------------------------

            if self._contains_youtube_words(rest_words):
                query_words = self._remove_youtube_markers(rest_words)
                query = " ".join(query_words).strip()

                if not query:
                    return None

                return Command(
                    skill_id="youtube.search",
                    arguments={"query": query}
                )

            # ----------------------------------------------
            # "открой сайт ..."
            # ----------------------------------------------

            if rest_words[0] == "сайт":
                site_query = " ".join(rest_words[1:]).strip()

                if not site_query:
                    return None

                return Command(
                    skill_id="browser.open_site",
                    arguments={"site": site_query}
                )

            # ----------------------------------------------
            # "открой ссылку ..." / похоже на URL
            # ----------------------------------------------

            looks_like_url = (
                "." in rest
                and " " not in rest
            )

            if rest_words[0] == "ссылку" or looks_like_url:
                url_value = rest

                if rest_words[0] == "ссылку":
                    url_value = " ".join(rest_words[1:]).strip()

                if not url_value:
                    return None

                return Command(
                    skill_id="browser.open_url",
                    arguments={"url": url_value}
                )

            # ----------------------------------------------
            # Обычное открытие программы.
            # ----------------------------------------------

            return Command(
                skill_id="system.open_program",
                arguments={"name": rest}
            )

        # ==================================================
        # CLOSE
        # ==================================================

        if category == "close":

            if not rest:
                return None

            return Command(
                skill_id="system.close_program",
                arguments={"name": rest}
            )

        # ==================================================
        # SEND
        # ==================================================

        if category == "send":

            if len(rest_words) < 2:
                return None

            recipient = rest_words[0]
            message_text = " ".join(rest_words[1:]).strip()

            if not message_text:
                return None

            return Command(
                skill_id="telegram.send_message",
                arguments={
                    "recipient": recipient,
                    "text": message_text,
                }
            )

        return None

    # ==================================================
    # SEARCH PARSER
    # ==================================================

    def _parse_search(self, words: list) -> Command | None:
        if not words:
            return None

        working_words = list(words)
        working_words = self._remove_preposition(working_words)

        has_youtube = self._contains_youtube_words(working_words)
        has_video = self._contains_video_words(working_words)

        query_words = self._remove_video_markers(working_words)
        query_words = self._remove_youtube_markers(query_words)

        query = " ".join(query_words).strip()

        if not query:
            return None

        if has_video or has_youtube:
            return Command(
                skill_id="youtube.search",
                arguments={"query": query}
            )

        return Command(
            skill_id="browser.search",
            arguments={"query": query}
        )

    # ==================================================
    # ACTION MATCHING
    # ==================================================

    def _match_action(self, action: str) -> tuple | None:
        all_words = {
            word: "open"
            for word in self.OPEN_WORDS
        }

        all_words.update({
            word: "close"
            for word in self.CLOSE_WORDS
        })

        all_words.update({
            word: "search"
            for word in self.SEARCH_WORDS
        })

        all_words.update({
            word: "send"
            for word in self.SEND_WORDS
        })

        if action in all_words:
            return all_words[action], action

        close = difflib.get_close_matches(
            action,
            all_words.keys(),
            n=1,
            cutoff=self.MATCH_CUTOFF,
        )

        if close:
            matched_word = close[0]
            return all_words[matched_word], matched_word

        return None

    # ==================================================
    # WORD HELPERS
    # ==================================================

    @staticmethod
    def _contains_video_words(words: list) -> bool:
        return any(
            word in CommandParser.VIDEO_WORDS
            for word in words
        )

    @staticmethod
    def _contains_youtube_words(words: list) -> bool:
        return any(
            word in CommandParser.YOUTUBE_WORDS
            for word in words
        )

    @staticmethod
    def _remove_video_markers(words: list) -> list:
        return [
            word
            for word in words
            if word not in CommandParser.VIDEO_WORDS
        ]

    @staticmethod
    def _remove_youtube_markers(words: list) -> list:
        youtube_words = {
            "ютуб",
            "youtube",
            "ютубе",
            "youtube.com",
        }

        return [
            word
            for word in words
            if word not in youtube_words
        ]

    @staticmethod
    def _remove_preposition(words: list) -> list:
        """
        Убирает "на"/"в" только если следом идёт
        упоминание YouTube — иначе оставляет
        предлог на месте, чтобы не портить
        обычные запросы вроде "кино на вечер".
        """

        youtube_markers = {"ютуб", "ютубе", "youtube"}
        result = []

        for i, word in enumerate(words):
            if word in {"на", "в"}:
                next_word = words[i + 1] if i + 1 < len(words) else None
                if next_word in youtube_markers:
                    continue
            result.append(word)

        return result