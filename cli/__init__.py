import click
from cli.registry import SITE_REGISTRY, OTHER_REGISTRY, SITE_CONFIG_REGISTRY
from .base_commands import show_about,show_version,config_call_back


@click.group()
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
    "-v","--version",
    is_flag=True,
    expose_value=False,
    help="Show info about this program",
    callback=show_version,
)
def cli():
    pass


for site_name, command_factory in SITE_REGISTRY.items():
    site_group = command_factory()

    config_key = f"{site_name}_config"
    if config_key in SITE_CONFIG_REGISTRY:
        config_factory = SITE_CONFIG_REGISTRY[config_key]
        site_group.add_command(config_factory(), name="config")

    cli.add_command(site_group, name=site_name)

for name, factory in OTHER_REGISTRY.items():
    cli.add_command(factory(), name=name)

if __name__ == "__main__":
    cli()
