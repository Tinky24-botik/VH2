import importlib.util
import json
from pathlib import Path

from interfaces.plugin import Plugin
from core.skill_registry import SkillRegistry


class PluginManager:

    def __init__(
        self,
        plugins_dir: str = "plugins",
        skill_registry: SkillRegistry | None = None
    ):
        self.plugins_dir = Path(plugins_dir)
        self.skill_registry = skill_registry or SkillRegistry()

        self.plugins: dict[str, Plugin] = {}
        self.plugin_skills: dict[str, list] = {}

    def discover_plugins(self) -> list[dict]:
        """
        Ищет плагины в папке plugins/.

        Каждый plugin должен содержать manifest.json.
        """

        discovered = []

        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True)
            return discovered

        for plugin_dir in self.plugins_dir.iterdir():

            if not plugin_dir.is_dir():
                continue

            manifest_path = plugin_dir / "manifest.json"

            if not manifest_path.exists():
                continue

            try:
                with open(
                    manifest_path,
                    "r",
                    encoding="utf-8"
                ) as file:
                    manifest = json.load(file)

                manifest["_path"] = plugin_dir

                discovered.append(manifest)

            except (json.JSONDecodeError, OSError) as error:
                print(
                    f"[PluginManager] Ошибка чтения "
                    f"{plugin_dir.name}: {error}"
                )

        return discovered

    def load_plugin(self, manifest: dict) -> bool:
        """
        Загружает один plugin.

        Ошибка одного plugin не ломает приложение.
        """

        plugin_id = manifest.get("id")
        plugin_entry = manifest.get("entry")

        if not plugin_id:
            print(
                "[PluginManager] Plugin без ID пропущен"
            )
            return False

        if plugin_id in self.plugins:
            print(
                f"[PluginManager] Plugin '{plugin_id}' "
                f"уже загружен"
            )
            return False

        if not plugin_entry:
            print(
                f"[PluginManager] {plugin_id}: "
                f"отсутствует entry"
            )
            return False

        plugin_dir = Path(manifest["_path"])
        plugin_file = plugin_dir / plugin_entry

        if not plugin_file.exists():
            print(
                f"[PluginManager] {plugin_id}: "
                f"файл {plugin_entry} не найден"
            )
            return False

        try:
            module_name = (
                f"voicehelper_plugin_{plugin_id}"
            )

            spec = importlib.util.spec_from_file_location(
                module_name,
                plugin_file
            )

            if spec is None or spec.loader is None:
                raise ImportError(
                    "Не удалось создать module spec"
                )

            module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(module)

            plugin_class = getattr(
                module,
                "PluginImpl"
            )

            plugin = plugin_class()

            if not isinstance(plugin, Plugin):
                raise TypeError(
                    "PluginImpl должен наследоваться "
                    "от Plugin"
                )

            plugin.initialize()

            skills = plugin.get_skills()

            registered_skills = []

            try:
                for skill in skills:
                    self.skill_registry.register(skill)
                    registered_skills.append(skill)

            except Exception:
                for skill in registered_skills:
                    self.skill_registry.unregister(
                        skill.skill_id
                    )

                plugin.shutdown()
                raise

            self.plugins[plugin_id] = plugin
            self.plugin_skills[plugin_id] = skills

            print(
                f"[PluginManager] Загружен: "
                f"{plugin_id}"
            )

            return True

        except Exception as error:
            print(
                f"[PluginManager] Не удалось загрузить "
                f"{plugin_id}: {error}"
            )

            return False

    def load_all(self) -> None:
        """
        Загружает все найденные plugins.
        """

        for manifest in self.discover_plugins():
            self.load_plugin(manifest)

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Выгружает один plugin и все его skills.
        """

        plugin = self.plugins.get(plugin_id)

        if plugin is None:
            return False

        skills = self.plugin_skills.get(
            plugin_id,
            []
        )

        for skill in skills:
            self.skill_registry.unregister(
                skill.skill_id
            )

        try:
            plugin.shutdown()

        except Exception as error:
            print(
                f"[PluginManager] Ошибка выключения "
                f"{plugin_id}: {error}"
            )

        del self.plugins[plugin_id]
        self.plugin_skills.pop(plugin_id, None)

        print(
            f"[PluginManager] Выгружен: "
            f"{plugin_id}"
        )

        return True

    def shutdown_all(self) -> None:
        """
        Выгружает все plugins.
        """

        for plugin_id in list(self.plugins):
            self.unload_plugin(plugin_id)

    def get_plugin(
        self,
        plugin_id: str
    ) -> Plugin | None:
        """
        Получить загруженный plugin по ID.
        """

        return self.plugins.get(plugin_id)

    def get_plugin_ids(self) -> list[str]:
        """
        Возвращает ID загруженных plugins.
        """

        return list(self.plugins.keys())