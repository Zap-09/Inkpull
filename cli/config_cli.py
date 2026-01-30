import click

from click_option_group import optgroup, AllOptionGroup

from inkpull.config import GConfig

def to_dict(key: str, value: str | None) -> dict:
    if key is None:
        raise ValueError("Key cannot be None")
    return {key: value}


def config_command():
    @click.command()
    @optgroup.group("set_key", cls=AllOptionGroup)
    @optgroup.option("-s", "--set", "set_key", type=str, help="adds a config value")
    @optgroup.option("-v", "--value", "set_value", type=str, help="adds a config value")
    # New group
    @optgroup.group("delete_key")
    @optgroup.option("-d", "--delete", "delete_key", type=str, help="deletes a config value")
    def config(set_key: str, set_value: str, delete_key: str):
        """
        Manages Global config values.
        """
        if delete_key:
            GConfig.delete_key(delete_key)
            return


        GConfig.update_key(to_dict(set_key, set_value))

    return config
