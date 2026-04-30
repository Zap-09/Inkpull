import pkgutil
import importlib
import inspect

import cli.sites as sites_pkg


def discover_site_commands():
    registry = {}

    for module_info in pkgutil.iter_modules(sites_pkg.__path__):
        module_name = module_info.name
        module = importlib.import_module(f"{sites_pkg.__name__}.{module_name}")

        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name.endswith("_command"):
                site_name = name.removesuffix("_command")
                registry[site_name] = obj

    return registry


SITE_REGISTRY = discover_site_commands()
