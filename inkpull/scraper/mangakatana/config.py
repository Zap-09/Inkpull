from ...config import BaseSiteConfig


class MangakatanaConfig(BaseSiteConfig):
    SITE_NAME = "Mangakatana"
    DEFAULTS = {
        "download_folder": "Mangakatana",
        "headers": {},
        "impersonate_browser": "default",
        "cookies": {
            "s_r": "sv2"
        },
        "metadata_file_name": "default",
        "metadata_style": "default"
    }
