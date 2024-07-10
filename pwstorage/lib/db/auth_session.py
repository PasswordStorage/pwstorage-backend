"""AuthSessionModel CRUD."""

from datetime import datetime, timezone
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from pwstorage.core.exceptions.auth_session import AuthSessionDeletedException, AuthSessionNotFoundException
from pwstorage.lib.models import AuthSessionModel, UserModel
from pwstorage.lib.schemas.auth_session import AuthSessionPaginationResponse, AuthSessionSchema
from pwstorage.lib.schemas.enums.redis import AuthRedisKeyType
from pwstorage.lib.schemas.pagination import PaginationRequest
from pwstorage.lib.utils.pagination import add_pagination_to_query, get_rows_count_in


async def get_auth_session_model(
    db: AsyncSession,
    *,
    session_id: UUID | None = None,
    user_id: int | None = None,
    refresh_token: UUID | None = None,
    join_user: bool = False,
    join_user_settings: bool = False,
    ignore_deleted: bool = False,
) -> AuthSessionModel:
    """Get a auth session model.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        session_id (UUID): Session ID, using with user_id.
        user_id (int): User ID, using with session_id.
        refresh_token (UUID): Refresh token.
        join_user (bool): Whether to join the user.
        join_user_settings (bool): Whether to join the user settings.

    Returns:
        AuthSessionModel: AuthSessionModel object.
    """
    query = select(AuthSessionModel)
    if session_id:
        query = query.where(AuthSessionModel.id == session_id, AuthSessionModel.user_id == user_id)
    if refresh_token:
        query = query.where(AuthSessionModel.refresh_token == refresh_token)
    if join_user:
        join_query = [joinedload(AuthSessionModel.user)]
        if join_user_settings:
            join_query.append(joinedload(AuthSessionModel.user).joinedload(UserModel.settings))
        query = query.options(*join_query)

    result = (await db.execute(query)).scalar_one_or_none()

    if result is None:
        raise AuthSessionNotFoundException
    elif not ignore_deleted and result.deleted_at is not None:
        raise AuthSessionDeletedException

    return result


async def create_auth_session(
    db: AsyncSession,
    user_id: int,
    user_ip: str,
    user_agent: str | None,
    fingerprint: str,
) -> AuthSessionModel:
    """Create auth session."""
    auth_session_model = AuthSessionModel(
        user_id=user_id, user_ip=user_ip, user_agent=user_agent, fingerprint=fingerprint
    )
    db.add(auth_session_model)
    await db.flush()
    return auth_session_model


async def get_auth_sessions(
    db: AsyncSession, user_id: int, pagination: PaginationRequest
) -> AuthSessionPaginationResponse:
    """Get auth sessions."""
    query_filter = (AuthSessionModel.user_id == user_id, AuthSessionModel.deleted_at.is_(None))
    query = select(AuthSessionModel).where(*query_filter)
    query_count = select(func.count(AuthSessionModel.id).filter(*query_filter))
    query = add_pagination_to_query(query, pagination)

    auth_sessions = (await db.execute(query)).scalars().all()
    total_items, pages = await get_rows_count_in(db, query_count, pagination.limit)

    items = [AuthSessionSchema.model_construct(**auth_session.to_dict()) for auth_session in auth_sessions]
    return AuthSessionPaginationResponse.model_construct(total_items=total_items, total_pages=pages, items=items)


async def get_auth_session(db: AsyncSession, auth_session_id: UUID, user_id: int) -> AuthSessionSchema:
    """Get auth session."""
    auth_session_model = await get_auth_session_model(db, session_id=auth_session_id, user_id=user_id)
    return AuthSessionSchema.model_construct(**auth_session_model.to_dict())


async def delete_auth_session(
    db: AsyncSession,
    redis: Redis,
    user_ip: str,
    user_agent: str | None,
    session: UUID | AuthSessionModel,
    user_id: int,
) -> None:
    """Delete auth session."""
    auth_session_model = (
        session
        if isinstance(session, AuthSessionModel)
        else (await get_auth_session_model(db, session_id=session, user_id=user_id))
    )
    await redis.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))
    if user_ip:
        auth_session_model.last_online = datetime.now(timezone.utc)
        auth_session_model.user_ip = user_ip
    if user_agent:
        auth_session_model.user_agent = user_agent
    auth_session_model.access_token = None
    auth_session_model.refresh_token = None
    auth_session_model.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def delete_user_sessions(db: AsyncSession, redis: Redis, user_id: int) -> None:
    """Delete user auth sessions."""
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
