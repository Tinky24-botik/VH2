from core.notifier import notify
from core.sound import play_success, play_error

FAILURE_MARKERS = (
    "Не знаю",
    "Не указан",
    "Не найден",
    "Ошибка выполнения",
    "Неизвестная команда",
    "Не понял",
)


def give_feedback(text: str):
    is_failure = any(
        text.startswith(marker)
        for marker in FAILURE_MARKERS
    )

    if is_failure:
        notify(text, kind="error")
        play_error()
    else:
        notify(text, kind="success")
        play_success()