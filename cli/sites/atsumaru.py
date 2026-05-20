import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup

from inkpull.scraper import Atsumaru_main


def atsumaru_command():
    @click.group(invoke_without_command=True)
    @optgroup.group("Download", cls=MutuallyExclusiveOptionGroup)
    @optgroup.option("-s", "--series", help="URL for series")
    @optgroup.option("-c", "--chapter", help="URL for a chapter")
    @optgroup.group("Scanlation flags")
    @optgroup.option("-sm", "--smart", "smart_selection",
                     help="Enable smart chapter selection from scanlation group. So no duplicate chapters",
                     default=False, is_flag=True)
    @optgroup.option("-a", "--all", "select_all",
                     help="Enable all chapter selection from all scanlation group.", default=False,
                     is_flag=True)
    @click.pass_context
    def atsumaru(ctx, series, chapter, smart_selection, select_all):
        mode = "series" if series else "chapter"
        url = series or chapter
        if ctx.invoked_subcommand is None:
            Atsumaru_main(url=url, mode=mode, smart_select=smart_selection, select_all=select_all)

    return atsumaru
