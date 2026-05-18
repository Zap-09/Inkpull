import json
import re
from pathlib import Path

from utils import log
from .metadata_style import StyleMixin
from ..config.runtime import GConfig


class BaseTemplate(StyleMixin):
    def __init__(self, config):
        if config is None:
            raise ValueError("Config must be provided")

        self.Config = config
        self.GConfig = GConfig
        self.project_root = self.find_project_root()

    def generate_metadata(self, **kwargs):
        """ Generate metadata structure based on the style. """
        style = self.Config.find("metadata_style")
        return self._build_metadata(style, **kwargs)

    def create_metadata_file(self,
                             file_path: Path | str,
                             data: dict,
                             *,
                             filename: str | Path | None = None) -> None:
        """ Create metadata file and save it to disc"""

        if filename is None:
            config_file_name = self.Config.find("metadata_file_name")
        else:
            config_file_name = filename

        config_file_name = Path(config_file_name).with_suffix(".json")

        file_path = Path(file_path) / config_file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json_data = json.dumps(data,
                                   indent=4,
                                   ensure_ascii=self.GConfig.global_get("ensure_ascii", False))
            f.write(json_data)

    def site_folder(self) -> Path:
        """ Returns sanitized site folder path """
        global_path_str = self.GConfig.global_get("Download_location")
        site_path_str = self.Config.find("download_folder")

        global_path = Path(global_path_str)
        site_path = Path(site_path_str)

        if not site_path.is_absolute() and ("/" in site_path_str or "\\" in site_path_str):
            folder_parts = re.split(r"[\\/]", site_path_str)
            site_path = Path(*folder_parts)

        if site_path.is_absolute():
            return self.sanitize_path(site_path)

        if global_path.is_absolute():
            final_path = global_path / site_path
        else:
            final_path = self.project_root / global_path / site_path

        return self.sanitize_path(final_path)

    def sanitize_path(self, path: Path | str) -> Path:
        path = Path(path)

        anchor = path.anchor

        sanitized_parts = [
            self.clean_folder_name(p)
            for p in path.parts
            if p not in (".", "..", anchor)
        ]

        if anchor:
            return Path(anchor, *sanitized_parts)

        return Path(*sanitized_parts)

    def save_cover(self, cover_url: str,
                   save_location: Path | str,
                   cover_bytes: bytes
                   ):
        """ Saves cover image"""
        ext = Path(cover_url).suffix or ".jpg"
        save_folder = self.sanitize_path(save_location)
        file_name = save_folder / f"Cover{ext}"
        file_name.parent.mkdir(parents=True, exist_ok=True)
        with open(file_name, "wb") as f:
            f.write(cover_bytes)
        log("Cover Downloaded", "info")
