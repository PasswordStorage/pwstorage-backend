"""App dependencies constructors."""

from json import loads as json_loads
from typing import Any, AsyncGenerator, Generator
from uuid import UUID

from jwt import InvalidTokenError
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from pwstorage.core.config import AppConfig
from pwstorage.core.exceptions.abc import UnauthorizedException
from pwstorage.core.security import Encryptor
from pwstorage.lib.schemas.auth import TokenRedisData
from pwstorage.lib.schemas.enums.redis import AuthRedisKeyType


def config() -> AppConfig:
    """Get application config.

    Returns:
        AppConfig: The application configuration loaded from environment variables.
    """
    return AppConfig.from_env()


def encryptor(config: AppConfig) -> Encryptor:
    """Get Encryptor instance.

    Args:
        config (AppConfig): The application configuration containing security settings.

    Returns:
        Encryptor: An instance of the Encryptor class.
    """
    return Encryptor(
        config.security.secret_key,
        config.jwt.algorithm,
        config.jwt.access_token_expire_minutes,
    )


def db_url(config: AppConfig) -> str:
    """Get database engine string.

    Args:
        config (AppConfig): The application configuration containing the database URL.

    Returns:
        str: The database URL.
    """
    return config.database.url


def db_engine(database_url: str) -> AsyncEngine:
    """Create database engine.

    Args:
        database_url (str): The database URL.

    Returns:
        AsyncEngine: The created asynchronous database engine.
    """
    return create_async_engine(database_url, isolation_level="SERIALIZABLE")


def db_session_maker(engine: AsyncEngine | str) -> Generator[sessionmaker[Any], None, None]:
    """Create database session maker.

    Args:
        engine (AsyncEngine | str): The database engine or URL.

    Yields:
        Generator[sessionmaker[Any], None, None]: A sessionmaker instance for creating database sessions.
    """
    engine = engine if isinstance(engine, AsyncEngine) else db_engine(engine)
    maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore[call-overload]
    yield maker
    maker.close_all()


async def db_session(maker: sessionmaker[Any]) -> AsyncGenerator[AsyncSession, None]:
    """Create database session.

    Args:
        maker (sessionmaker[Any]): The sessionmaker instance for creating database sessions.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session.
    """
    session = maker()
    try:
        yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()


async def db_session_autocommit(maker: sessionmaker[Any]) -> AsyncGenerator[AsyncSession, None]:
    """Create database session with auto commit on successful execution.

    Args:
        maker (sessionmaker[Any]): The sessionmaker instance for creating database sessions.

    Yields:
        AsyncGenerator[AsyncSession, None]: An asynchronous database session.
    """
    session = maker()
    try:
        yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()


def redis_url(config: AppConfig) -> str:
    """Get Redis URL.

    Args:
        config (AppConfig): The application configuration containing the Redis URL.

    Returns:
        str: The Redis URL.
    """
    return config.redis.url


async def redis_pool(redis_url: str) -> AsyncGenerator[ConnectionPool, None]:
    """Create Redis connection pool.

    Args:
        redis_url (str): The Redis URL.

    Yields:
        AsyncGenerator[ConnectionPool, None]: A Redis connection pool.
    """
    pool = ConnectionPool.from_url(redis_url)
    yield pool
    await pool.aclose()


async def redis_conn(pool: ConnectionPool) -> AsyncGenerator[Redis, None]:
    """Create Redis connection.

    Args:
        pool (ConnectionPool): The Redis connection pool.

    Yields:
        AsyncGenerator[Redis, None]: A Redis connection.
    """
    conn = Redis(connection_pool=pool)
    try:
        yield conn
    finally:
        await conn.aclose()


async def get_token_data(encryptor: Encryptor, redis: Redis, token: str) -> TokenRedisData:
    """Get token data.

    Args:
        encryptor (Encryptor): The Encryptor instance for decoding the JWT.
        redis (Redis): The Redis connection.
        token (str): The JWT token.

    Returns:
        TokenData: The token data.

    Raises:
        UnauthorizedException: If the token is invalid or not found in Redis.
    """
    payload = _decode_jwt(encryptor, token)
    str_data = await redis.get(AuthRedisKeyType.access.format(payload.get("sub")))

    if str_data is None:
        raise UnauthorizedException(detail_="Invalid token")

    return TokenRedisData.model_construct(**json_loads(str_data))


def get_refresh_token(encryptor: Encryptor, token: str) -> UUID:
    """Get refresh token.

    Args:
        encryptor (Encryptor): The Encryptor instance for decoding the JWT.
        token (str): The JWT token.

    Returns:
        UUID: The refresh token.

    Raises:
        UnauthorizedException: If the token is invalid.
    """
    payload = _decode_jwt(encryptor, token)

    try:
        return UUID(payload.get("sub"))
    except (ValueError, TypeError, AttributeError):
        raise UnauthorizedException(detail_="Invalid refresh token")


def _decode_jwt(encryptor: Encryptor, token: str) -> dict[str, Any]:
    """Decode JWT.

    Args:
        encryptor (Encryptor): The Encryptor instance for decoding the JWT.
        token (str): The JWT token.

    Returns:
        dict[str, Any]: The decoded JWT payload.

    Raises:
        UnauthorizedException: If the token is invalid.
    """
    try:
        return encryptor.decode_jwt(token)
    except InvalidTokenError:
        raise UnauthorizedException(detail_="Invalid token")
