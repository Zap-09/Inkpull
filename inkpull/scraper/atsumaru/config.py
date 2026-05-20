from ...config import BaseSiteConfig


class AtsumaruConfig(BaseSiteConfig):
    SITE_NAME = "atsumaru"
    DEFAULTS = {
        "download_folder": "Atsumaru",
        "user-agent": "",
        "headers": {
            "Referer": "https://atsu.moe/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        },
        "impersonate_browser": "default",
        "cookies": {},
        "metadata_file_name": "default",
        "metadata_style": "default",
    }
