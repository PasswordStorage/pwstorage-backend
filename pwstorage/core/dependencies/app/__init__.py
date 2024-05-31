"""App dependencies."""

from typing import Annotated

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from pwstorage.core.config import AppConfig

from . import fastapi


AppConfigDependency = Annotated[AppConfig, *fastapi.AppConfigDependency.__metadata__]
SessionDependency = Annotated[AsyncSession, *fastapi.SessionDependency.__metadata__]
RedisDependency = Annotated[Redis, *fastapi.RedisDependency.__metadata__]

__all__ = [
    "AppConfigDependency",
    "SessionDependency",
    "RedisDependency",
]
