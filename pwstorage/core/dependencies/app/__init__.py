"""App dependencies."""

from typing import Annotated
from uuid import UUID

from fastapi import Header
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from pwstorage.core.config import AppConfig
from pwstorage.core.security import Encryptor
from pwstorage.lib.schemas.auth import TokenData

from . import fastapi


AppConfigDependency = Annotated[AppConfig, *fastapi.AppConfigDependency.__metadata__]
EncryptorDependency = Annotated[Encryptor, *fastapi.EncryptorDependency.__metadata__]
SessionDependency = Annotated[AsyncSession, *fastapi.SessionDependency.__metadata__]
RedisDependency = Annotated[Redis, *fastapi.RedisDependency.__metadata__]
ClientHostDependency = Annotated[str, *fastapi.ClientHostDependency.__metadata__]
TokenDataDependency = Annotated[TokenData, *fastapi.TokenDataDependency.__metadata__]
RefreshTokenDependency = Annotated[UUID, *fastapi.RefreshTokenDependency.__metadata__]

UserAgentDependency = Annotated[str, Header()]

__all__ = [
    "AppConfigDependency",
    "EncryptorDependency",
    "SessionDependency",
    "RedisDependency",
    "ClientHostDependency",
    "TokenDataDependency",
    "RefreshTokenDependency",
    "UserAgentDependency",
]
