"""AuthSession CRUD."""

from datetime import datetime, timezone
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from pwstorage.core.exceptions.session import AuthSessionDeletedException, AuthSessionNotFoundException
from pwstorage.lib.models import AuthSessionModel
from pwstorage.lib.schemas.enums.redis import AuthRedisKeyType


async def get_auth_session_model(
    db: AsyncSession,
    *,
    session_id: UUID | None = None,
    refresh_token: UUID | None = None,
    join_user: bool = False,
    ignore_deleted: bool = False,
) -> AuthSessionModel:
    """Get a auth session model.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        session_id (UUID): Session ID.
        refresh_token (UUID): Refresh token.
        join_user (bool): Whether to join the user.

    Returns:
        AuthSessionModel: AuthSessionModel object.
    """
    query = select(AuthSessionModel)
    if session_id:
        query = query.where(AuthSessionModel.id == session_id)
    if refresh_token:
        query = query.where(AuthSessionModel.refresh_token == refresh_token)
    if join_user:
        query = query.options(joinedload(AuthSessionModel.user))
    result = (await db.execute(query)).scalar_one_or_none()

    if result is None:
        raise AuthSessionNotFoundException
    elif not ignore_deleted and result.deleted_at is not None:
        raise AuthSessionDeletedException

    return result


async def delete_session(
    db: AsyncSession, redis: Redis, user_ip: str, user_agent: str | None, session: UUID | AuthSessionModel
) -> None:
    """Delete token."""
    auth_session_model = (
        session if isinstance(session, AuthSessionModel) else (await get_auth_session_model(db, session_id=session))
    )
    await redis.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))
    auth_session_model.user_ip = user_ip
    auth_session_model.user_agent = user_agent
    auth_session_model.access_token = None
    auth_session_model.refresh_token = None
    auth_session_model.last_online = datetime.now(timezone.utc)
    auth_session_model.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def delete_user_sessions(db: AsyncSession, redis: Redis, user_id: int) -> None:
    """Delete user sessions."""
    query = select(AuthSessionModel).where(AuthSessionModel.user_id == user_id, AuthSessionModel.deleted_at.is_(None))
    result = (await db.execute(query)).scalars().all()
    redis_pipe = redis.pipeline()

    for auth_session_model in result:
        redis_pipe.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))
        auth_session_model.access_token = None
        auth_session_model.refresh_token = None
        auth_session_model.deleted_at = datetime.now(timezone.utc)

    await redis_pipe.execute()
    await db.flush()
