import os
import json
from dotenv import load_dotenv
from telethon.sync import TelegramClient

from interfaces.skill import Skill
from core.fuzzy_match import find_match, NeedsConfirmation

load_dotenv()


class TelegramSendMessageSkill(Skill):

    @property
    def skill_id(self) -> str:
        return "telegram.send_message"

    @property
    def name(self) -> str:
        return "Отправка сообщения в Telegram"

    def execute(self, **kwargs):
        contact_name = kwargs.get("recipient")
        text = kwargs.get("text")
        confirmed = kwargs.get("confirmed", False)
        exclude = kwargs.get("exclude", set())

        if not contact_name or not text:
            return "Не указан получатель или текст сообщения"

        contacts = self._load_contacts()
        contact_name_lower = contact_name.lower()

        match = find_match(
            contact_name_lower,
            contacts,
            exclude=exclude,
        )

        if match.value is None:
            return (
                f"Не знаю контакт «{contact_name}», "
                f"добавь его в settings.json"
            )

        if match.needs_confirmation and not confirmed:
            return NeedsConfirmation(
                question=f"Ты имел в виду «{match.matched_key}»?",
                skill_id=self.skill_id,
                arguments={
                    "recipient": contact_name,
                    "text": text,
                },
                guessed_key=match.matched_key,
            )

        api_id = int(os.getenv("TELEGRAM_API_ID"))
        api_hash = os.getenv("TELEGRAM_API_HASH")

        with TelegramClient(
            "voicehelper_session",
            api_id,
            api_hash
        ) as client:
            client.send_message(match.value, text)

        if match.matched_key != contact_name_lower:
            return (
                f"Отправил сообщение для {match.matched_key} "
                f"(расслышал как «{contact_name}»)"
            )

        return f"Отправил сообщение для {match.matched_key}"

    def _load_contacts(self):
        with open(
            "config/settings.json",
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)
        return data.get("contacts", {})