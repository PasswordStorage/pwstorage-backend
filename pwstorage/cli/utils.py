"""Utility commands."""

from asyncio import run

import click

from pwstorage.core.config import AppConfig

from .cli import cli


try:
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    from pwstorage.lib.models.abc import AbstractModel
except ImportError:
    pass


@cli.group()
def utils() -> None:  # noqa D103
    pass


async def _init_dev_db() -> None:
    """Initialize dev database."""
    config = AppConfig.from_env()
    engine = create_async_engine(config.database.url)
    maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore
    session: AsyncSession = maker()
    async with session.begin():
        session.add_all([])
        await session.flush()


@utils.command()
def init_dev_db() -> None:
    """Initialize dev database."""
    run(_init_dev_db())


async def _reset_db() -> None:
    """Reset database."""
    config = AppConfig.from_env()
    engine = create_async_engine(config.database.url)
    async with engine.begin() as conn:
        await conn.run_sync(AbstractModel.metadata.drop_all)


@utils.command()
@click.option("--i-am-completely-sure-that-i-want-to-do-this", is_flag=True)
def reset_db(i_am_completely_sure_that_i_want_to_do_this: bool) -> None:
    """Reset database."""
    accepted = i_am_completely_sure_that_i_want_to_do_this
    if not accepted:
        confirmation = input("Are you sure you want to reset the database? [y/N] ")
        if confirmation.lower() != "y":
            return
        accepted = True

    if accepted:
        run(_reset_db())
