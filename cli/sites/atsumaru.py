import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup, RequiredAllOptionGroup

from inkpull.scraper import Atsumaru_main
from inkpull.scraper.atsumaru.config import AtsumaruConfig
from utils import log


def atsumaru_command():
    @optgroup.group("Download", cls=MutuallyExclusiveOptionGroup)
    @click.group(invoke_without_command=True)
    @optgroup.option("-s", "--series", help="URL for series")
    @optgroup.option("-c", "--chapter", help="URL for a chapter")
    @optgroup.group("Group")
    @optgroup.option("-g", "--group",
                     help="Pick the scanlation group. Keep empty for all groups",default=None)
    @click.pass_context
    def atsumaru(ctx, series, chapter,group):
        mode = "series" if series else "chapter"
        url = series or chapter
        if ctx.invoked_subcommand is None:
            Atsumaru_main(url=url, mode=mode,scan_group=group)

    return atsumaru


def atsumaru_config_command():
    @click.command()
    @optgroup.group("Actions", cls=RequiredAllOptionGroup)
    @optgroup.option("-s", "--set", "set_key")
    @optgroup.option("-v", "--value", "value_key")
    # Another Group
    @optgroup.group("Delete")
    @optgroup.option("-d", "--delete", "delete_key", help="Delete a config key")
    def config(set_key, value_key, delete_key):
        atsumaru_config = AtsumaruConfig()

        if set_key and value_key:
            atsumaru_config.update_key(set_key, value_key)
        elif delete_key:
            atsumaru_config.delete_key(delete_key)
        else:
            log("Invalid flag combinations","error")

    return config
