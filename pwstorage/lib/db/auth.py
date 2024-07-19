"""Auth CRUD."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from pwstorage.core.exceptions.auth import BadAuthDataException, BadFingerprintException
from pwstorage.core.security import Encryptor
from pwstorage.lib.db import auth_session as auth_session_db, user as user_db
from pwstorage.lib.models import AuthSessionModel
from pwstorage.lib.schemas.auth import TokenCreateSchema, TokenRedisData, TokenRefreshSchema, TokenSchema
from pwstorage.lib.schemas.enums.redis import AuthRedisKeyType


def raise_user_password(password: str, password_hash: str) -> None:
    """Raise an exception if the user password is incorrect.

    Args:
        password (str): The user's password.
        password_hash (str): The hashed password stored in the database.

    Raises:
        BadAuthDataException: If the password is incorrect.
    """
    if Encryptor.hash_password(password) != password_hash:
        raise BadAuthDataException


async def create_token(
    db: AsyncSession,
    redis: Redis,
    encryptor: Encryptor,
    user_ip: str,
    user_agent: str | None,
    schema: TokenCreateSchema,
) -> TokenSchema:
    """Create a new token.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        redis (Redis): Redis connection.
        encryptor (Encryptor): Encryptor instance for encoding JWT.
        user_ip (str): User IP address.
        user_agent (str | None): User agent.
        schema (TokenCreateSchema): Schema containing token creation data.

    Returns:
        TokenSchema: The created token schema.
    """
    user_model = await user_db.get_user_model(db, user_email=schema.email, join_settings=True)
    raise_user_password(schema.password, user_model.password_hash)

    auth_session_model = await auth_session_db.create_auth_session(
        db,
        user_id=user_model.id,
        user_ip=user_ip,
        user_agent=user_agent,
        fingerprint=Encryptor.hash_password(schema.fingerprint),
    )

    await _create_access_token(
        redis,
        auth_session_model,
        access_token_id=auth_session_model.access_token,
        expires_in=encryptor.jwt_expire_minutes,
    )

    return TokenSchema(
        access_token=encryptor.encode_jwt(auth_session_model.access_token),
        refresh_token=encryptor.encode_jwt(
            auth_session_model.refresh_token, expires_in=user_model.settings.auth_session_expiration
        ),
        access_token_expires_in=encryptor.jwt_expire_minutes,
        refresh_token_expires_in=user_model.settings.auth_session_expiration,
    )


async def refresh_token(
    db: AsyncSession,
    redis: Redis,
    encryptor: Encryptor,
    user_ip: str,
    user_agent: str | None,
    token_id: UUID,
    schema: TokenRefreshSchema,
) -> TokenSchema:
    """Refresh an existing token.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        redis (Redis): Redis connection.
        encryptor (Encryptor): Encryptor instance for encoding JWT.
        user_ip (str): User IP address.
        user_agent (str | None): User agent.
        token_id (UUID): Token ID.
        schema (TokenRefreshSchema): Schema containing token refresh data.

    Returns:
        TokenSchema: The refreshed token schema.
    """
    auth_session_model = await auth_session_db.get_auth_session_model(
        db, refresh_token=token_id, join_user=True, join_user_settings=True
    )

    await redis.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))

    auth_session_model.user_ip = user_ip
    auth_session_model.user_agent = user_agent
    auth_session_model.last_online = datetime.now(timezone.utc)

    if Encryptor.hash_password(schema.fingerprint) != auth_session_model.fingerprint:
        auth_session_model.access_token = None
        auth_session_model.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        raise BadFingerprintException

    auth_session_model.access_token = await _create_access_token(
        redis, auth_session_model, expires_in=encryptor.jwt_expire_minutes
    )
    auth_session_model.refresh_token = uuid4()
    await db.flush()

    return TokenSchema(
        access_token=encryptor.encode_jwt(auth_session_model.access_token),
        refresh_token=encryptor.encode_jwt(
            auth_session_model.refresh_token, expires_in=auth_session_model.user.settings.auth_session_expiration
        ),
        access_token_expires_in=encryptor.jwt_expire_minutes,
        refresh_token_expires_in=auth_session_model.user.settings.auth_session_expiration,
    )


async def _create_access_token(
    redis: Redis, auth_session_model: AuthSessionModel, *, access_token_id: UUID | None = None, expires_in: int = 30
) -> UUID:
    """Create an access token and store it in Redis.

    Args:
        redis (Redis): Redis connection.
        auth_session_model (AuthSessionModel): Auth session model.
        access_token_id (UUID | None, optional): Access token ID. Defaults to None.
        expires_in (int, optional): Expiration time in minutes. Defaults to 30.

    Returns:
        UUID: The created access token ID.
    """
    access_token_id = access_token_id or uuid4()
    await redis.set(
        AuthRedisKeyType.access.format(access_token_id),
        TokenRedisData(
            session_id=auth_session_model.id,
            user_id=auth_session_model.user_id,
            encryption_key=Encryptor.hash_password(auth_session_model.user.password_hash[-32:], digest_size=32),
        ).model_dump_json(),
        ex=expires_in * 60,
    )
    return access_token_id
