from ...config import BaseSiteConfig


class WeebCentralConfig(BaseSiteConfig):
    SITE_NAME = "WeebCentral"
    DEFAULTS = {
        "download_folder": "WeebCentral",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "headers": {
            "Referer": "",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        },
        "impersonate_browser": "firefox",
        "cookies": {

        },
        "metadata_file_name": "details",
        "metadata_style": "mihon"
    }