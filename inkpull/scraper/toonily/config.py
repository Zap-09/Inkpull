from ...config import GConfig
from utils import log


class ToonilyConfig:
    DEFAULTS = {
        "download_folder": "Toonily",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "headers": {
            "Referer": "https://toonily.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        },
        "impersonate_browser": "firefox",
        "cookies": {
            "toonily-mature": "1",
            "toonily-lazyload": "off"
        },
        "metadata_file_name": "details",
        "metadata_style": "mihon"
    }

    def __init__(self):
        self.config = GConfig
        self._settings: dict = self.config.ensure_site("toonily")
        self.ensure_defaults()

    def ensure_defaults(self):
        updated = False
        for key, value in self.DEFAULTS.items():
            if key not in self._settings:
                self._settings[key] = value
                updated = True
        if updated:
            log("Some configs were missing(Toonily), updating...", "warn")
            self.config.save()
            log("Toonily site defaults added", "info")

    def find(self, key, default=None):
        return self._settings.get(key, default)

    def update_key(self, key, value):
        self._settings[key] = value
        self.config.save()
        log(f"Toonily config updated: {key}", "info")

    def delete_key(self, key_name: str):
        result = self._settings.pop(key_name, None)
        if result is None:
            log("Config key not found in config", "warn")
        else:
            log(f"Successfully deleted config key '{key_name}'", "info")
