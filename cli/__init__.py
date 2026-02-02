import click
from cli.registry import SITE_REGISTRY, OTHER_REGISTRY, SITE_CONFIG_REGISTRY
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


for name in sorted(OTHER_REGISTRY):
    cli.add_command(OTHER_REGISTRY[name](), name=name)


for site_name in sorted(SITE_REGISTRY):
    site_group = SITE_REGISTRY[site_name]()

    if site_name in SITE_CONFIG_REGISTRY:
        site_group.add_command(
            SITE_CONFIG_REGISTRY[site_name](),
            name="config"
        )

    cli.add_command(site_group, name=site_name)


if __name__ == "__main__":
    cli()
