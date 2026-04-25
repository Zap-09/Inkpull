from inkpull.config.runtime import GConfig
from utils import log


class BaseSiteConfig:
    SITE_NAME: str | None = None
    DEFAULTS: dict = {}

    def __init__(self):
        if not self.SITE_NAME or not isinstance(self.SITE_NAME, str):
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
        value = self._settings.get(key, "default")
        if value == "default":
            return self.config.global_get(key, default)

        return value

    def update_key(self, key, value):
        self._settings[key] = value
        self.config.save()
        log(f"{self.site_name} config updated: {key}", "info")
