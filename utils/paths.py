import sys
import subprocess
from pathlib import Path

from .terminal import log
from .environment_variables import env


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


def open_config_file():
    env_path = env.CONFIG_PATH

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
