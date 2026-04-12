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

