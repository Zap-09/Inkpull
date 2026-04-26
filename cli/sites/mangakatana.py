import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
from inkpull import Mangakatana_main


def mangakatana_command():
    @click.group(invoke_without_command=True)
    @optgroup.group("Download", cls=MutuallyExclusiveOptionGroup)
    @optgroup.option("-s", "--series", help="URL for series")
    @optgroup.option("-c", "--chapter", help="URL for a chapter")
    @click.pass_context
    def mangakatana(ctx, series, chapter):
        mode = "series" if series else "chapter"
        url = series or chapter
        if ctx.invoked_subcommand is None:
            Mangakatana_main(url=url, mode=mode)

    return mangakatana
