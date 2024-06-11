"""Auth CRUD."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from pwstorage.core.exceptions.auth import BadAuthDataException, BadFingerprintException
from pwstorage.core.security import Encryptor
from pwstorage.lib.db import user as user_db
from pwstorage.lib.models import AuthSessionModel
from pwstorage.lib.schemas.auth import TokenCreateSchema, TokenData, TokenRefreshSchema, TokenSchema
from pwstorage.lib.schemas.enums.redis import AuthRedisKeyType

from .auth_session import create_auth_session, get_auth_session_model


def raise_user_password(password: str, password_hash: str) -> None:
    """Raise for user password.

    Raises:
        BadAuthDataException: Bad password.
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
    """Create token."""
    user_model = await user_db.get_user_model(db, user_email=schema.email)
    raise_user_password(schema.password, user_model.password_hash)

    auth_session_model = await create_auth_session(
        db,
        user_id=user_model.id,
        user_ip=user_ip,
        user_agent=user_agent,
        fingerprint=schema.fingerprint,
        expires_in=schema.expires_in,
    )

    await _create_access_token(redis, auth_session_model, access_token_id=auth_session_model.access_token)

    return TokenSchema(
        access_token=encryptor.encode_jwt(auth_session_model.access_token),
        refresh_token=encryptor.encode_jwt(auth_session_model.refresh_token, expires_in=auth_session_model.expires_in),
        access_token_expires_in=encryptor.jwt_expire_minutes,
        refresh_token_expires_in=auth_session_model.expires_in,
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
    """Refresh token."""
    auth_session_model = await get_auth_session_model(db, refresh_token=token_id, join_user=True)

    await redis.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))

    auth_session_model.user_ip = user_ip
    auth_session_model.user_agent = user_agent
    auth_session_model.last_online = datetime.now(timezone.utc)

    if schema.fingerprint != auth_session_model.fingerprint:
        auth_session_model.access_token = None
        auth_session_model.refresh_token = None
        auth_session_model.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        raise BadFingerprintException

    auth_session_model.access_token = await _create_access_token(redis, auth_session_model)
    auth_session_model.refresh_token = uuid4()
    await db.flush()

    return TokenSchema(
        access_token=encryptor.encode_jwt(auth_session_model.access_token),
        refresh_token=encryptor.encode_jwt(auth_session_model.refresh_token, expires_in=auth_session_model.expires_in),
        access_token_expires_in=encryptor.jwt_expire_minutes,
        refresh_token_expires_in=auth_session_model.expires_in,
    )


async def _create_access_token(
    redis: Redis, auth_session_model: AuthSessionModel, *, access_token_id: UUID | None = None, expires_in: int = 30
) -> UUID:
    access_token_id = access_token_id or uuid4()
    await redis.set(
        AuthRedisKeyType.access.format(access_token_id),
        TokenData(
            session_id=auth_session_model.id,
            user_id=auth_session_model.user_id,
            encryption_key=Encryptor.hash_password(auth_session_model.user.password_hash[-32:], digest_size=32),
        ).model_dump_json(),
        ex=expires_in * 60,
    )
    return access_token_id
