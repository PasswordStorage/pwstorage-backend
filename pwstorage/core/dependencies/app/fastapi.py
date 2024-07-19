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
from pwstorage.lib.schemas.auth import TokenRedisData

from . import constructors as app_depends


def app_config_stub() -> AppConfig:
    """Get app config stub.

    Raises:
        NotImplementedError: This is a stub function and should be implemented.

    Returns:
        AppConfig: The application configuration.
    """
    raise NotImplementedError


def encryptor(config: Annotated[AppConfig, Depends(app_config_stub)]) -> Encryptor:
    """Get Encryptor instance.

    Args:
        config (AppConfig): The application configuration containing security settings.

    Returns:
        Encryptor: An instance of the Encryptor class.
    """
    return app_depends.encryptor(config)


def db_session_maker_stub() -> sessionmaker[Any]:
    """Get database session maker stub.

    Raises:
        NotImplementedError: This is a stub function and should be implemented.

    Returns:
        sessionmaker[Any]: The sessionmaker instance for creating database sessions.
    """
    raise NotImplementedError


async def db_session(
    request: Request, maker: Annotated[sessionmaker[Any], Depends(db_session_maker_stub)]
) -> AsyncGenerator[AsyncSession, None]:
    """Get database session.

    Args:
        request (Request): The FastAPI request object.
        maker (sessionmaker[Any]): The sessionmaker instance for creating database sessions.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session.
    """
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
    """Get Redis connection pool stub.

    Raises:
        NotImplementedError: This is a stub function and should be implemented.

    Returns:
        ConnectionPool: The Redis connection pool.
    """
    raise NotImplementedError


async def redis_conn(
    request: Request, conn_pool: Annotated[ConnectionPool, Depends(redis_conn_pool_stub)]
) -> AsyncGenerator[AbstractRedis, None]:
    """Get Redis connection.

    Args:
        request (Request): The FastAPI request object.
        conn_pool (ConnectionPool): The Redis connection pool.

    Yields:
        AsyncGenerator[AbstractRedis, None]: A Redis connection.
    """
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
    """Get client host.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        str: The client's host address.
    """
    client = request.client
    return client.host if client else ""


async def get_token_data(
    encryptor: Annotated[Encryptor, Depends(encryptor)],
    redis: Annotated[AbstractRedis, Depends(redis_conn)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> TokenRedisData:
    """Get token data.

    Args:
        encryptor (Encryptor): The Encryptor instance for decoding the JWT.
        redis (AbstractRedis): The Redis connection.
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials.

    Returns:
        TokenData: The token data.

    Raises:
        UnauthorizedException: If the token is invalid or not found in Redis.
    """
    return await app_depends.get_token_data(encryptor, redis, credentials.credentials)


def get_refresh_token(
    encryptor: Annotated[Encryptor, Depends(encryptor)],
    refresh_token: Annotated[str | None, Cookie()],
) -> UUID:
    """Get refresh token from cookies.

    Args:
        encryptor (Encryptor): The Encryptor instance for decoding the JWT.
        refresh_token (str | None): The refresh token from cookies.

    Returns:
        UUID: The refresh token.

    Raises:
        UnauthorizedException: If the token is invalid.
    """
    return app_depends.get_refresh_token(encryptor, refresh_token or "")


AppConfigDependency = Annotated[AppConfig, Depends(app_config_stub)]
EncryptorDependency = Annotated[Encryptor, Depends(encryptor)]
SessionDependency = Annotated[AsyncSession, Depends(db_session)]
RedisDependency = Annotated[AbstractRedis, Depends(redis_conn)]
ClientHostDependency = Annotated[str, Depends(get_client_host)]
TokenDataDependency = Annotated[TokenRedisData, Depends(get_token_data)]
RefreshTokenDependency = Annotated[UUID, Depends(get_refresh_token)]
