from ...config import BaseSiteConfig


class ToonilyConfig(BaseSiteConfig):
    SITE_NAME = "toonily"
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
