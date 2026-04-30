import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup

from inkpull.scraper import Atsumaru_main


def atsumaru_command():
    @click.group(invoke_without_command=True)
    @optgroup.group("Download", cls=MutuallyExclusiveOptionGroup)
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

