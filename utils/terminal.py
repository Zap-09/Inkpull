from typing import Literal


def log(msg: str,
        level: Literal["info", "warn", "error", "conf"] = "info",
        *,
        _return: bool = False,
        _end="\n",
        _noformat:bool = False):
    """
    Logs a message to the terminal with color based on level.

    Args:
        msg (str): The message to log.
        level (str, optional): One of "info", "warn", "error", "conf". Default is "info".
        _return (bool, optional): Whether to return the message or print it. Defaults to False.
        _end (str, optional): The end of the message. Defaults to "\n".
        _noformat (bool, optional): Whether to add the level prefix
    """
    colors = {
        "info": "\033[92m",  # Green
        "warn": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "conf": "\033[34m",  # Blue
    }

    reset = "\033[0m"

    level: str = level.lower()
    color = colors.get(level, colors["info"])

    if _noformat:
        message = f"{color}{msg}{reset}"
    else:
        message = f"{color}[{level.upper()}] {msg}{reset}"

    if _return:
        return message
    else:
        print(message, end=_end)
        return None


def user_confirmation(msg: str):
    msg = f"{msg} (y/N): "
    while True:
        user_response = input(
            log(msg, level="conf", _return=True)
        ).lower()
        match user_response:
            case "y":
                return True
            case "n" | "":
                return False
            case _:
                log("Invalid response. Try again.", "error")
