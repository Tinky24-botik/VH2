import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

with TelegramClient("voicehelper_session", api_id, api_hash) as client:
    print("Авторизация прошла успешно, сессия сохранена.")