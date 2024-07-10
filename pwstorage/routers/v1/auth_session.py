"""Auth session endpoints."""

from uuid import UUID

from fastapi import APIRouter
from pyfa_converter_v2 import QueryDepends

from pwstorage.core.dependencies.app import RedisDependency, SessionDependency, TokenDataDependency
from pwstorage.core.exceptions.auth_session import AuthSessionDeletedException, AuthSessionNotFoundException
from pwstorage.lib.db import auth_session as auth_session_db
from pwstorage.lib.schemas.auth_session import AuthSessionPaginationResponse, AuthSessionSchema
from pwstorage.lib.schemas.pagination import PaginationRequest
from pwstorage.lib.utils.openapi import exc_list


router = APIRouter(tags=["auth session"], prefix="/auth_sessions")


@router.get("/", response_model=AuthSessionPaginationResponse)
async def get_auth_sessions(
    db: SessionDependency,
    token_data: TokenDataDependency,
    pagination: PaginationRequest = QueryDepends(PaginationRequest),
) -> AuthSessionPaginationResponse:
    """Get auth sessions."""
    return await auth_session_db.get_auth_sessions(db, token_data.user_id, pagination)


@router.get(
    "/{auth_session_id}",
    response_model=AuthSessionSchema,
    openapi_extra=exc_list(AuthSessionNotFoundException, AuthSessionDeletedException),
)
async def get_auth_session(
    db: SessionDependency, token_data: TokenDataDependency, auth_session_id: UUID
) -> AuthSessionSchema:
    """Get auth session."""
    return await auth_session_db.get_auth_session(db, auth_session_id, token_data.user_id)


@router.delete(
    "/{auth_session_id}",
    status_code=204,
    openapi_extra=exc_list(AuthSessionNotFoundException, AuthSessionDeletedException),
)
async def delete_auth_session(
    db: SessionDependency, redis: RedisDependency, token_data: TokenDataDependency, auth_session_id: UUID
) -> None:
    """Delete auth session."""
    return await auth_session_db.delete_auth_session(db, redis, "", "", auth_session_id, token_data.user_id)
