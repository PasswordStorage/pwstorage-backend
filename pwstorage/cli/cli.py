"""Module with main CLI function."""

import click

from pwstorage.lib.utils.log import configure_logging


@click.group()
def cli() -> None:
    """Control interface for pwstorage API."""
    configure_logging()
