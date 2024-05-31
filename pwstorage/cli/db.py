"""Database-related commands."""

import alembic.config

from .cli import cli


@cli.group()
def db() -> None:
    """Database management commands."""
    pass


@db.command()
def migrate() -> None:
    """Run the alembic migrations."""
    alembic.config.main(argv=["--raiseerr", "upgrade", "head"])


@db.command()
def upgrade() -> None:
    """Run next alembic migration."""
    alembic.config.main(argv=["--raiseerr", "upgrade", "+1"])


@db.command()
def downgrade() -> None:
    """Run previous alembic migration."""
    alembic.config.main(argv=["--raiseerr", "downgrade", "-1"])
