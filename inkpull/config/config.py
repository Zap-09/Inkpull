import json
import os
from pathlib import Path
from utils import log, find_project_root


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

    def __init__(self, path: Path | None = None):
        self.path: str | Path = path or self.config_file_path
        self._config = {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                try:
                    self._config = json.load(f)
                    if not isinstance(self._config, dict):
                        log("Config file invalid: root is not a dict, resetting", "warn")
                        self._config = {}
                except json.JSONDecodeError:
                    log("Config file is empty or invalid JSON, initializing empty config", "warn")
                    self._config = {}
        except FileNotFoundError:
            log("Config file not found, initializing empty config", "warn")
            self._config = {}

        self.ensure_defaults()

    def ensure_defaults(self):
        updated = False
        for key, value in self.DEFAULTS.items():
            if key not in self._config:
                self._config[key] = value
                updated = True

        if updated:
            self.save()
            log("Looks like some of the config keys are missing.", "warn")
            log("Default config values added", "warn")

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

    def delete_key(self,key_name:str):
        result = self._config.pop(key_name, None)
        if result is None:
            log("Config key not found in config", "warn")
        else:
            log(f"Successfully deleted config key '{key_name}'","info")


_global_config_instance = None

def get_global_config():
    global _global_config_instance
    if _global_config_instance is None:
        _global_config_instance = GlobalConfig()
    return _global_config_instance
