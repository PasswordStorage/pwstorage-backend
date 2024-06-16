"""UserModel CRUD."""

from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from pwstorage.core.exceptions.user import UserDeletedException, UserEmailAlreadyExistsException, UserNotFoundException
from pwstorage.core.security import Encryptor
from pwstorage.lib.models import UserModel
from pwstorage.lib.schemas.user import UserCreateSchema, UserPatchSchema, UserSchema, UserUpdateSchema

from . import auth_session as auth_session_db, folder as folder_db, settings as settings_db


async def is_email_exists(db: AsyncSession, email: str) -> bool:
    """Check if user email already exists."""
    query = select(UserModel).where(UserModel.email == email, UserModel.deleted_at.is_(None))
    return bool((await db.execute(query)).scalar_one_or_none())


async def raise_for_user_email(db: AsyncSession, email: str) -> None:
    """Raise for user email.

    Raises:
        UserEmailAlreadyExistsException: User email already exists.
    """
    if await is_email_exists(db, email):
        raise UserEmailAlreadyExistsException(email=email)


async def get_user_model(
    db: AsyncSession,
    *,
    user_id: int | None = None,
    user_email: str | None = None,
    join_settings: bool = False,
    ignore_deleted: bool = False,
) -> UserModel:
    """Get a user model.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID.
        user_email (str): User email.

    Returns:
        UserModel: UserModel object.
    """
    query = select(UserModel)
    if user_id:
        query = query.where(UserModel.id == user_id)
    if user_email:
        query = query.where(UserModel.email == user_email, UserModel.deleted_at.is_(None))
    if join_settings:
        query = query.options(joinedload(UserModel.settings))
    result = (await db.execute(query)).scalar_one_or_none()

    if result is None:
        raise UserNotFoundException
    elif not ignore_deleted and result.deleted_at is not None:
        raise UserDeletedException

    return result


async def create_user(db: AsyncSession, schema: UserCreateSchema) -> UserSchema:
    """Create user."""
    await raise_for_user_email(db, schema.email)

    user_model = UserModel(
        **schema.model_dump(exclude={"password"}), password_hash=Encryptor.hash_password(schema.password)
    )
    db.add(user_model)

    await db.flush()
    await settings_db.create_settings(db, user_model.id)

    return UserSchema.model_construct(**user_model.to_dict())


async def get_user(db: AsyncSession, user_id: int) -> UserSchema:
    """Get user."""
    user_model = await get_user_model(db, user_id=user_id)
    return UserSchema.model_construct(**user_model.to_dict())


async def update_user(db: AsyncSession, user_id: int, schema: UserUpdateSchema | UserPatchSchema) -> UserSchema:
    """Update user."""
    user_model = await get_user_model(db, user_id=user_id)

    if schema.email and schema.email != user_model.email:
        await raise_for_user_email(db, schema.email)

    for field, value in schema.iterate_set_fields():
        setattr(user_model, field, value)

    await db.flush()
    return UserSchema.model_construct(**user_model.to_dict())


async def delete_user(db: AsyncSession, redis: Redis, user_id: int) -> None:
    """Delete user."""
    user_model = await get_user_model(db, user_id=user_id)
    user_model.deleted_at = datetime.now(timezone.utc)
    await settings_db.delete_user_settings(db, user_id)
    await auth_session_db.delete_user_sessions(db, redis, user_id)
    await folder_db.delete_user_foldes(db, user_id)
