import click
from cli.registry import SITE_REGISTRY
from .base_commands import show_about, show_version, config_call_back

class OrderedGroup(click.Group):
    def list_commands(self, ctx):
        return list(self.commands)


@click.group(cls=OrderedGroup)
@click.option(
    "--config",
    is_flag=True,
    expose_value=False,
    help="Open the config file",
    callback=config_call_back,
)
@click.option(
    "--about",
    is_flag=True,
    expose_value=False,
    help="Show info about this program",
    callback=show_about,
)
@click.option(
    "-v", "--version",
    is_flag=True,
    expose_value=False,
    help="Show info about this program",
    callback=show_version,
)
def cli():
    pass


for site_name in sorted(SITE_REGISTRY):
    site_group = SITE_REGISTRY[site_name]()
    cli.add_command(site_group, name=site_name)

if __name__ == "__main__":
    cli()
