import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup

from inkpull.scraper import MangaTaro_main

def mangataro_command():
    @click.group(invoke_without_command=True)
    @optgroup.group("Download", cls=MutuallyExclusiveOptionGroup)
    @optgroup.option("-s", "--series", help="URL for series")
    @optgroup.option("-c", "--chapter", help="URL for a chapter")
    @click.pass_context
    def mangataro(ctx, series, chapter):
        mode = "series" if series else "chapter"
        url = series or chapter
        if ctx.invoked_subcommand is None:
            MangaTaro_main(url=url, mode=mode)

    return mangataro

