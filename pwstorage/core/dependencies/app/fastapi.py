"""Dependency injection annotations for the agent module."""

from typing import Annotated, Any, AsyncGenerator
from uuid import UUID

from fastapi import Cookie, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import ConnectionPool, Redis as AbstractRedis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from pwstorage.core.config import AppConfig
from pwstorage.core.security import Encryptor
from pwstorage.lib.schemas.auth import TokenData

from . import constructors as app_depends


def app_config_stub() -> AppConfig:
    """Get app config stub."""
    raise NotImplementedError


def encryptor(config: Annotated[AppConfig, Depends(app_config_stub)]) -> Encryptor:
    """Get Encryptor."""
    return app_depends.encryptor(config)


def db_session_maker_stub() -> sessionmaker[Any]:
    """Get database session maker stub."""
    raise NotImplementedError


async def db_session(
    request: Request, maker: Annotated[sessionmaker[Any], Depends(db_session_maker_stub)]
) -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    generator = app_depends.db_session_autocommit(maker)
    session = await anext(generator)
    request.state.db = session

    yield session

    try:
        await anext(generator)
    except StopAsyncIteration:
        pass
    else:
        raise RuntimeError("Database session not closed (db dependency generator is not closed).")


def redis_conn_pool_stub() -> ConnectionPool:
    """Get redis connection pool stub."""
    raise NotImplementedError


async def redis_conn(
    request: Request, conn_pool: Annotated[ConnectionPool, Depends(redis_conn_pool_stub)]
) -> AsyncGenerator[AbstractRedis, None]:
    """Get redis connection."""
    generator = app_depends.redis_conn(conn_pool)
    redis = await anext(generator)
    request.state.redis = redis

    yield redis

    try:
        await anext(generator)
    except StopAsyncIteration:
        pass
    else:
        raise RuntimeError("Redis session not closed (redis dependency generator is not closed).")


def get_client_host(request: Request) -> str:
    """Get client host."""
    client = request.client
    return client.host if client else ""


async def get_token_data(
    encryptor: Annotated[Encryptor, Depends(encryptor)],
    redis: Annotated[AbstractRedis, Depends(redis_conn)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> TokenData:
    """Get token data."""
    return await app_depends.get_token_data(encryptor, redis, credentials.credentials)


def get_refresh_token(
    encryptor: Annotated[Encryptor, Depends(encryptor)],
    refresh_token: Annotated[str | None, Cookie()],
) -> UUID:
    """Get refresh token from cookies."""
    return app_depends.get_refresh_token(encryptor, refresh_token or "")


AppConfigDependency = Annotated[AppConfig, Depends(app_config_stub)]
EncryptorDependency = Annotated[Encryptor, Depends(encryptor)]
SessionDependency = Annotated[AsyncSession, Depends(db_session)]
RedisDependency = Annotated[AbstractRedis, Depends(redis_conn)]
ClientHostDependency = Annotated[str, Depends(get_client_host)]
TokenDataDependency = Annotated[TokenData, Depends(get_token_data)]
RefreshTokenDependency = Annotated[UUID, Depends(get_refresh_token)]
