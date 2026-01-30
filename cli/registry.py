from .sites import toonily_command, toonily_config_command
from .sites import weebcentral_command, weebcentral_config_command

from .config_cli import config_command

SITE_REGISTRY = {
    "toonily": toonily_command,
    "weebcentral": weebcentral_command
}

OTHER_REGISTRY = {
    "config": config_command
}

SITE_CONFIG_REGISTRY = {
    "toonily_config": toonily_config_command,
    "weebcentral_config": weebcentral_config_command
}
