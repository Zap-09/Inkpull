from .sites import *

from .config_cli import config_command

SITE_REGISTRY = {
    "atsumaru": atsumaru_command,
    "toonily": toonily_command,
    "weebcentral": weebcentral_command
}

OTHER_REGISTRY = {
    "config": config_command
}


SITE_CONFIG_REGISTRY = {
    "atsumaru": atsumaru_config_command,
    "toonily": toonily_config_command,
    "weebcentral": weebcentral_config_command
}
