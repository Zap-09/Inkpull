import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup, RequiredAllOptionGroup

from inkpull.scraper import Toonily_main
from inkpull.scraper.toonily.config import ToonilyConfig
from utils import log


def toonily_command():
    @optgroup.group("Download", cls=MutuallyExclusiveOptionGroup)
    @click.group(invoke_without_command=True)
    @optgroup.option("-s", "--series", help="URL for series")
    @optgroup.option("-c", "--chapter", help="URL for series")
    @click.pass_context
    def toonily(ctx, series, chapter):
        mode = "series" if series else "chapter"
        url = series or chapter
        if ctx.invoked_subcommand is None:
            Toonily_main(url=url, mode=mode)

    return toonily


def toonily_config_command():
    @click.command()
    @optgroup.group("Actions", cls=RequiredAllOptionGroup)
    @optgroup.option("-s", "--set", "set_key")
    @optgroup.option("-v", "--value", "value_key")
    # Another Group
    @optgroup.group("Delete")
    @optgroup.option("-d", "--delete", "delete_key", help="Delete a config key from toonily")
    def config(set_key, value_key, delete_key):
        toonily_config = ToonilyConfig()

        if set_key and value_key:
            toonily_config.update_key(set_key, value_key)
        elif delete_key:
            toonily_config.delete_key(delete_key)
        else:
            log("Invalid flag combinations","error")

    return config
