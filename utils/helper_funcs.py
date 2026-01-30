import re
import sys
import os
import subprocess
from pathlib import Path

from .terminal import log


def clean_folder_name(name: str) -> str:
    """ Removes invalid Characters in folder/file name """

    invalid_chars = r"[\/:*?\"<>|]"
    name = re.sub(invalid_chars, " ", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


def find_project_root() -> Path:
    """
    Returns the directory where inkpull.exe (or main.py) lives.
    This will serve as the "root" for downloads and config.
    """
    if getattr(sys, "_MEIPASS", None):
        exe_path = Path(sys.executable).resolve()
        return exe_path.parent
    else:
        return Path(sys.argv[0]).resolve().parent


def remove_dupes_in_list(*all_lists: list):
    """ Removes duplicate items in lists """
    big_list = []
    seen = set()
    for lst in all_lists:
        if lst is None:
            continue
        for i in lst:
            if i not in seen:
                big_list.append(i)
                seen.add(i)
    return big_list


def flatten(iterable):
    """ Flattens lists into lists """
    result = []

    for item in iterable:
        if isinstance(item, (list, tuple)):
            result.extend(flatten(item))
        else:
            result.append(str(item))

    return result


def open_config_file():
    env_path = os.getenv("comic_dl_config")

    if env_path:
        config_file_path = Path(env_path)
    else:
        config_file_path = find_project_root() / "config" / "config.json"

    if not config_file_path.exists():
        log(f"Config file not found at {config_file_path}", "error")
        return

    config_file_path = str(config_file_path)
    match sys.platform:
        case "win32":
            subprocess.run(["cmd", "/c", "start", "", config_file_path], check=True)
        case "darwin":
            subprocess.run(["open", config_file_path], check=True)
        case "linux":
            subprocess.run(["xdg-open", config_file_path], check=True)
        case _:
            log(f"Unknown platform:{sys.platform}", "error")
