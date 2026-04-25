from ...config import BaseSiteConfig


class MangaTaroConfig(BaseSiteConfig):
    SITE_NAME = "MangaTaro"
    DEFAULTS = {
        "download_folder": "MangaTaro",
        "headers":{
            "Referer": "https://mangataro.org",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        },
        "impersonate_browser": "default",
        "cookies": {},
        "metadata_file_name": "default",
        "metadata_style": "default"
    }