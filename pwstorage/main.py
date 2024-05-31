"""Main."""

import asyncio
from hashlib import sha256

from lib.models.abc import AbstractModel
from lib.models.user import UserModel
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine


async def main() -> None:  # noqa: D103
    engine = create_async_engine("postgresql+asyncpg://user:password@localhost/db")

    async with engine.begin() as conn:
        await conn.run_sync(AbstractModel.metadata.create_all)

        await conn.execute(
            insert(UserModel).values(
                name="Den", email="den@gmail.com", password_hash=sha256("DenPassword".encode()).hexdigest()
            )
        )
        await conn.execute(
            insert(UserModel).values(
                name="Nikita", email="nikita2005@gmail.com", password_hash=sha256("NikitaPassword".encode()).hexdigest()
            )
        )
        await conn.execute(
            insert(UserModel).values(
                name="Rarseni", email="rarseni@gmail.com", password_hash=sha256("RarseniPassword".encode()).hexdigest()
            )
        )
        await conn.execute(
            insert(UserModel).values(
                name="Danya", email="danya@gmail.com", password_hash=sha256("DanyaPassword".encode()).hexdigest()
            )
        )


asyncio.run(main())
