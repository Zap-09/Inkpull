import click
from utils import open_config_file

def config_call_back(ctx: click.Context, _param, value):
    if not value:
        return
    open_config_file()
    ctx.exit()


def show_about(ctx: click.Context, _param, value):
    if not value:
        return
    print(
        """Inkpull - A Comic downloader cli tool made with python
Copyright (c) 2026 Zap-09
Licensed under GNU General Public License v3.0 (GPL-3.0)

This program allows downloading comics from various websites via the command line.

Source code & full license: https://github.com/Zap-09/Inkpull

Disclaimer: This software is provided "as-is", without any warranty of any kind.
"""
    )
    ctx.exit()

def show_version(ctx: click.Context, _param, value):
    if not value:
        return
    from .app_metadata import Metadata
    print(Metadata.__version__)
    ctx.exit()
