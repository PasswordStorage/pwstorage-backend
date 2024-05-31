"""CLI commands for VMM API.

All commands must be re-exported in this module, to launch code execution.
"""

from . import run, utils


try:
    from . import db
except ModuleNotFoundError:
    pass

from .cli import cli


__all__ = ["cli", "run", "db", "utils"]
