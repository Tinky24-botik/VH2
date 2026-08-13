import json
import threading

from core.plugin_manager import PluginManager
from core.skill_registry import SkillRegistry
from core.router import CommandRouter
from core.command_parser import CommandParser
from core.command_processor import CommandProcessor
from core.notifier import start as start_notifier
from core.stt import VoiceListener


def main():
    # ==================================================
    # CORE
    # ==================================================

    skill_registry = SkillRegistry()

    plugin_manager = PluginManager(
        skill_registry=skill_registry
    )

    print("=== VoiceHelper ===")
    print()
    print("Загрузка plugins...")

    plugin_manager.load_all()

    print()
    print(
        f"Загружено plugins: "
        f"{len(plugin_manager.get_plugin_ids())}"
    )

    print(
        f"Доступно skills: "
        f"{len(skill_registry.get_all())}"
    )

    # ==================================================
    # ROUTER / PARSER / PROCESSOR
    # ==================================================

    router = CommandRouter(
        skill_registry=skill_registry
    )

    parser = CommandParser()

    processor = CommandProcessor(
        router=router,
        parser=parser,
    )

    # ==================================================
    # NOTIFIER
    # ==================================================

    start_notifier()

    # ==================================================
    # SETTINGS
    # ==================================================

    with open("config/settings.json", "r", encoding="utf-8") as f:
        app_settings = json.load(f)

    # ==================================================
    # VOICE
    # ==================================================

    voice_listener = VoiceListener(
        processor=processor,
        trigger_word=app_settings.get("trigger", "лёня"),
        small_model_path=app_settings.get("small_model_path", "model_small"),
        big_model_path=app_settings.get("model_path", "model"),
        stt_mode=app_settings.get("stt_mode", "auto"),
    )

    voice_listener.start()

    # ==================================================
    # TEXT INPUT
    # ==================================================

    print()
    print("Текстовый ввод активен.")
    print("Голосовой ввод активен.")
    print()
    print("Голос:")
    print("  «лёня» → затем команда")
    print("  или сразу «лёня открой хром»")
    print()
    print("Текст:")
    print("  пиши команду прямо сюда")
    print()
    print("Для выхода введи: выход")
    print()

    try:
        while True:
            try:
                text = input(">>> ").strip()

            except (KeyboardInterrupt, EOFError):
                print()
                break

            if text.lower() == "выход":
                break

            if not text:
                continue

            processor.process(text)

    finally:
        voice_listener.stop()
        plugin_manager.shutdown_all()


if __name__ == "__main__":
    main()