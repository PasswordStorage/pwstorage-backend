"""User endpoints."""

from fastapi import APIRouter

from pwstorage.core.dependencies.app import RedisDependency, SessionDependency, TokenDataDependency
from pwstorage.core.exceptions.user import UserEmailAlreadyExistsException
from pwstorage.lib.db import user as user_db
from pwstorage.lib.schemas.user import UserCreateSchema, UserPatchSchema, UserSchema, UserUpdateSchema
from pwstorage.lib.utils.openapi import exc_list


router = APIRouter(tags=["user"], prefix="/users")


@router.post("/", response_model=UserSchema, openapi_extra=exc_list(UserEmailAlreadyExistsException))
async def create_user(db: SessionDependency, schema: UserCreateSchema) -> UserSchema:
    """Create user."""
    return await user_db.create_user(db, schema)


@router.get("/me", response_model=UserSchema)
async def get_user(db: SessionDependency, token_data: TokenDataDependency) -> UserSchema:
    """Get user."""
    return await user_db.get_user(db, token_data.user_id)


@router.put("/me", response_model=UserSchema, openapi_extra=exc_list(UserEmailAlreadyExistsException))
async def update_user(db: SessionDependency, token_data: TokenDataDependency, schema: UserUpdateSchema) -> UserSchema:
    """Update user."""
    return await user_db.update_user(db, token_data.user_id, schema)


@router.patch("/me", response_model=UserSchema, openapi_extra=exc_list(UserEmailAlreadyExistsException))
async def patch_user(db: SessionDependency, token_data: TokenDataDependency, schema: UserPatchSchema) -> UserSchema:
    """Patch user."""
    return await user_db.update_user(db, token_data.user_id, schema)


@router.delete("/me", status_code=204)
async def delete_user(db: SessionDependency, redis: RedisDependency, token_data: TokenDataDependency) -> None:
    """Delete user."""
    return await user_db.delete_user(db, redis, token_data.user_id)
