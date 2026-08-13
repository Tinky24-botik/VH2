from core.router import CommandRouter, Command
from core.command_parser import CommandParser
from core.fuzzy_match import NeedsConfirmation, NeedsSelection
from core.selection import resolve_selection
from core.feedback import give_feedback
from core.notifier import notify


YES_WORDS = {
    "да",
    "ага",
    "верно",
    "точно",
    "правильно",
}

NO_WORDS = {
    "нет",
    "неа",
    "неправильно",
}


class CommandProcessor:
    """
    Единая точка обработки команд.

    Источник команды не имеет значения:
    - клавиатура;
    - Vosk;
    - другой STT;
    - Groq;
    - будущий голосовой движок.

    На вход всегда приходит обычная строка.

    CommandProcessor также хранит состояние
    незавершённого диалога:

    1. Обычная команда.
    2. Skill просит подтверждение.
    3. Skill предлагает несколько вариантов.
    4. Пользователь отвечает.
    5. CommandProcessor продолжает исходную операцию.
    """

    def __init__(
        self,
        router: CommandRouter,
        parser: CommandParser,
    ):
        self.router = router
        self.parser = parser

        # Здесь хранится незавершённая операция.
        #
        # Возможные значения:
        # None
        # NeedsConfirmation
        # NeedsSelection
        self.pending = None

    # ==================================================
    # YES / NO
    # ==================================================

    @staticmethod
    def is_yes(text: str) -> bool:
        """
        Проверяет, является ли ответ подтверждением.
        """

        normalized = (
            text
            .strip()
            .lower()
        )

        return normalized in YES_WORDS

    @staticmethod
    def is_no(text: str) -> bool:
        """
        Проверяет, является ли ответ отрицанием.
        """

        normalized = (
            text
            .strip()
            .lower()
        )

        return normalized in NO_WORDS

    # ==================================================
    # MAIN PROCESS
    # ==================================================

    def process(self, text: str):
        """
        Обрабатывает одну текстовую строку.

        Возвращает:

        - обычный результат Skill;
        - NeedsConfirmation;
        - NeedsSelection;
        - None, если команда не распознана.

        Один и тот же метод используется
        текстовым и голосовым вводом.
        """

        if text is None:
            return None

        text = str(text).strip()

        if not text:
            return None

        # --------------------------------------------------
        # Ожидаем подтверждение
        # --------------------------------------------------

        if isinstance(
            self.pending,
            NeedsConfirmation,
        ):
            return self._handle_confirmation(text)

        # --------------------------------------------------
        # Ожидаем выбор варианта
        # --------------------------------------------------

        if isinstance(
            self.pending,
            NeedsSelection,
        ):
            return self._handle_selection(text)

        # --------------------------------------------------
        # Обычная новая команда
        # --------------------------------------------------

        command = self.parser.parse(text)

        if command is None:
            message = "Не понял команду."

            print(message)
            give_feedback(message)

            return None

        result = self.router.route(command)

        return self._handle_result(result)

    # ==================================================
    # CONFIRMATION
    # ==================================================

    def _handle_confirmation(
        self,
        text: str,
    ):
        """
        Обрабатывает ответ на вопрос:

        «Ты имел в виду Chrome?»

        Например:

        да
        ага
        нет
        неа
        """

        pending = self.pending

        # --------------------------------------------------
        # Пользователь подтвердил
        # --------------------------------------------------

        if self.is_yes(text):

            result = self.router.route(
                Command(
                    skill_id=pending.skill_id,
                    arguments={
                        **pending.arguments,
                        "confirmed": True,
                    },
                )
            )

            self.pending = None

            return self._handle_result(result)

        # --------------------------------------------------
        # Пользователь отказался
        # --------------------------------------------------

        if self.is_no(text):

            result = self.router.route(
                Command(
                    skill_id=pending.skill_id,
                    arguments={
                        **pending.arguments,
                        "exclude": {
                            pending.guessed_key
                        },
                    },
                )
            )

            self.pending = None

            return self._handle_result(result)

        # --------------------------------------------------
        # Не поняли ответ
        # --------------------------------------------------

        message = (
            "Ответь «да» или «нет»."
        )

        print(message)

        notify(
            message,
            kind="info",
        )

        return message

    # ==================================================
    # SELECTION
    # ==================================================

    def _handle_selection(
        self,
        text: str,
    ):
        """
        Обрабатывает выбор пользователя
        из списка вариантов.

        Поддерживает как текстовый,
        так и голосовой ответ.

        Например:

        1
        2
        3

        второй
        третий
        первый вариант

        номер два
        вариант три

        """

        pending = self.pending

        # --------------------------------------------------
        # Пытаемся определить выбранный вариант
        # --------------------------------------------------

        selected = resolve_selection(
            text,
            pending.options,
        )

        # --------------------------------------------------
        # Не удалось определить выбор
        # --------------------------------------------------

        if selected is None:

            message = (
                "Не понял, какой вариант. "
                "Скажи, например, «первый», "
                "«второй» или назови номер."
            )

            print(message)

            notify(
                message,
                kind="info",
            )

            # ВАЖНО:
            #
            # Здесь мы НЕ сбрасываем pending.
            #
            # Это позволяет пользователю
            # повторить ответ голосом.
            #
            # Например:
            #
            # Assistant:
            #   Нашёл варианты 1, 2, 3...
            #
            # User:
            #   эээ...
            #
            # Assistant:
            #   Не понял...
            #
            # User:
            #   второй
            #
            # И выбор всё ещё существует.

            return message

        # --------------------------------------------------
        # Выбор найден
        # --------------------------------------------------

        result = self.router.route(
            Command(
                skill_id=pending.skill_id,
                arguments={
                    **pending.arguments,
                    "selected_index": selected,
                    "video_map": pending.video_map,
                },
            )
        )

        # Исходная операция завершена.
        self.pending = None

        return self._handle_result(result)

    # ==================================================
    # RESULT
    # ==================================================

    def _handle_result(
        self,
        result,
    ):
        """
        Обрабатывает результат Skill.

        Возможные варианты:

        обычный результат
            ↓
        выполнение завершено

        NeedsConfirmation
            ↓
        сохраняем состояние
        и ждём ответа пользователя

        NeedsSelection
            ↓
        сохраняем состояние
        и ждём выбора пользователя
        """

        # --------------------------------------------------
        # Требуется подтверждение
        # --------------------------------------------------

        if isinstance(
            result,
            NeedsConfirmation,
        ):

            self.pending = result

            print(
                result.question
            )

            notify(
                result.question,
                kind="info",
            )

            return result

        # --------------------------------------------------
        # Требуется выбор
        # --------------------------------------------------

        if isinstance(
            result,
            NeedsSelection,
        ):

            self.pending = result

            print(
                result.question
            )

            notify(
                result.question,
                kind="info",
            )

            return result

        # --------------------------------------------------
        # Обычный результат
        # --------------------------------------------------

        print(result)

        give_feedback(
            str(result)
        )

        return result

    # ==================================================
    # STATE
    # ==================================================

    def has_pending(self) -> bool:
        """
        Проверяет, есть ли незавершённая операция.

        Полезно для STT/голосового интерфейса.
        """

        return self.pending is not None

    def clear_pending(self) -> None:
        """
        Принудительно сбрасывает незавершённую операцию.
        """

        self.pending = None