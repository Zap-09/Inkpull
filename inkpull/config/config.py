import json
import os
from pathlib import Path
from utils import log, find_project_root, user_confirmation, GenericException


class GlobalConfig:
    DEFAULTS = {
        "chunk_size": 8192,
        "image_concurrency": 5,
        "timeout": 30,
        "Download_location": "Downloads",
        "impersonate_browser": "firefox",
        "ensure_ascii": False,
    }
    PROJECT_ROOT: Path = find_project_root()

    default_path: Path = PROJECT_ROOT / "config" / "config.json"
    env_path = os.getenv("inkpull_config")
    config_file_path = Path(env_path) if env_path else default_path

    config_file_path.parent.mkdir(parents=True, exist_ok=True)

    def __init__(self, path: Path | str | None = None):
        self.path: str | Path = path or self.config_file_path
        self._config: dict = {}

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
        except FileNotFoundError:
            log("Config file not found, initializing empty config", "warn")
            self.create_defaults()
            return

        if not raw:
            log("Config file is empty, initializing empty config", "warn")
            self.create_defaults()
            return

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            log("Invalid json file", "warn")
            if user_confirmation("Overwrite with default config?"):
                self.create_defaults()
                return
            else:
                raise GenericException.UserRejection(
                    "Cannot continue without a valid config file."
                )


        if not isinstance(data, dict):
            log("Config file invalid: root is not a dict.", "warn")
            if user_confirmation("Overwrite with default config?"):
                self.create_defaults()
                return
            else:
                raise GenericException.UserRejection(
                    "Cannot continue without a valid config file."
                )
        self._config = data

        self.ensure_defaults()

    def ensure_defaults(self):
        updated = False
        for key, value in self.DEFAULTS.items():
            if key not in self._config:
                self._config[key] = value
                updated = True

        if updated:
            self.save()
            log("Default config values added", "info")

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=4)

    def global_get(self, key, default=None):
        return self._config.get(key, default)

    def ensure_site(self, name: str):
        self._config.setdefault("sites", {})
        self._config["sites"].setdefault(name, {})
        return self._config["sites"][name]

    def create_defaults(self):
        self._config.update(self.DEFAULTS)
        self.save()
        log("Config defaults created", "info")

    def update_key(self, user_input: dict[str, str]):
        for key, value in user_input.items():
            self._config[key] = value
            log(f"Config updated: {key} = {value}", "info")
        self.save()

    def delete_key(self, key_name: str):
        result = self._config.pop(key_name, None)
        if result is None:
            log("Config key not found in config", "warn")
        else:
            log(f"Successfully deleted config key '{key_name}'", "info")


GConfig = GlobalConfig()


class BaseSiteConfig:
    SITE_NAME: str = None
    DEFAULTS: dict = {}

    def __init__(self):
        if not self.SITE_NAME:
            raise ValueError("SITE_NAME must be defined in subclass")

        self.site_name = self.SITE_NAME.lower()
        self.config = GConfig
        self._settings: dict = self.config.ensure_site(self.site_name)
        self.ensure_defaults()

    def ensure_defaults(self):
        updated = False
        for key, value in self.DEFAULTS.items():
            if key not in self._settings:
                self._settings[key] = value
                updated = True

        if updated:
            log(f"Some configs were missing ({self.site_name}), updating...", "warn")
            self.config.save()
            log(f"{self.site_name} site defaults added", "info")

    def find(self, key, default=None):
        return self._settings.get(key, default)

    def update_key(self, key, value):
        self._settings[key] = value
        self.config.save()
        log(f"{self.site_name} config updated: {key}", "info")

    def delete_key(self, key_name: str):
        result = self._settings.pop(key_name, None)
        if result is None:
            log("Config key not found in config", "warn")
        else:
            log(f"Successfully deleted config key '{key_name}'", "info")
