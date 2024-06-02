"""App dependencies constructors."""

from json import loads as json_loads
from typing import Any, AsyncGenerator, Generator
from uuid import UUID

from jwt import InvalidTokenError, decode as jwt_decode
from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from pwstorage.core.config import AppConfig, JWTConfig
from pwstorage.core.exceptions.abc import UnauthorizedException
from pwstorage.lib.schemas.auth import TokenData
from pwstorage.lib.schemas.enums.redis import AuthRedisKeyType


def config() -> AppConfig:
    """Get application config."""
    return AppConfig.from_env()


def db_url(config: AppConfig) -> str:
    """Get database engine string."""
    return config.database.url


def db_engine(database_url: str) -> AsyncEngine:
    """Create database engine."""
    return create_async_engine(database_url, isolation_level="SERIALIZABLE")


def db_session_maker(engine: AsyncEngine | str) -> Generator[sessionmaker[Any], None, None]:
    """Create database session maker."""
    engine = engine if isinstance(engine, AsyncEngine) else db_engine(engine)
    maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore[call-overload]
    yield maker
    maker.close_all()


async def db_session(maker: sessionmaker[Any]) -> AsyncGenerator[AsyncSession, None]:
    """Create database session."""
    session = maker()
    try:
        yield session
    except SQLAlchemyError:
        await session.rollback()
        raise
    finally:
        await session.close()


async def db_session_autocommit(maker: sessionmaker[Any]) -> AsyncGenerator[AsyncSession, None]:
    """Create database session with auto commit on successful execution."""
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
    """Get Redis URL."""
    return config.redis.url


async def redis_pool(redis_url: str) -> AsyncGenerator[ConnectionPool, None]:
    """Create Redis connection pool."""
    pool = ConnectionPool.from_url(redis_url)
    yield pool
    await pool.aclose()


async def redis_conn(pool: ConnectionPool) -> AsyncGenerator[Redis, None]:
    """Create Redis connection."""
    conn = Redis(connection_pool=pool)
    try:
        yield conn
    finally:
        await conn.aclose()


def decode_jwt(config: JWTConfig, token: str) -> dict[str, Any]:
    """Decode JWT."""
    try:
        return jwt_decode(token, key=config.secret_key, algorithms=[config.algorithm])
    except InvalidTokenError:
        raise UnauthorizedException(detail_="Invalid token")


async def get_token_data(config: JWTConfig, redis: Redis, token: str) -> TokenData:
    """Get token data."""
    payload = decode_jwt(config, token)
    str_data = await redis.get(AuthRedisKeyType.access.format(payload.get("sub")))

    if str_data is None:
        raise UnauthorizedException(detail_="Invalid token")

    return TokenData.model_construct(**json_loads(str_data))


def get_refresh_token(config: JWTConfig, token: str) -> UUID:
    """Get refresh token."""
    payload = decode_jwt(config, token)

    try:
        return UUID(payload.get("sub"))
    except (ValueError, TypeError, AttributeError):
        raise UnauthorizedException(detail_="Invalid refresh token")
