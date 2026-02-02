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
        "impersonate_browser": "firefox",
        "cookies": {},
        "metadata_file_name": "details",
        "metadata_style": "mihon",
        "scan_group":{
            "alpha": "cmgzlbh3i9vp3m19184ncw4ul",
            "asura": "cmkzi8aln001a20nvithv7arz",
        },
        "scan_group_warn": True,
    }
