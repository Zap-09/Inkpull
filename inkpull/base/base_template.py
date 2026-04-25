import json
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
        return (self.find_project_root() /
                self.clean_folder_name(self.GConfig.global_get("Download_location")) /
                self.clean_folder_name(self.Config.find("download_folder")))

    def sanitize_path(self, path: Path | str, project_root: Path | str | None = None) -> Path:
        """ Sanitizes an absolute path. If input is not an absolute path it just sanitizes the input"""

        if project_root is None:
            project_root = self.project_root
        else:
            project_root = Path(project_root)

        path = Path(path)
        if not path.is_absolute():
            return Path(self.clean_folder_name(str(path)))

        relative_path = path.relative_to(project_root)

        sanitized_parts = [self.clean_folder_name(p) for p in relative_path.parts]
        return project_root.joinpath(*sanitized_parts)

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
