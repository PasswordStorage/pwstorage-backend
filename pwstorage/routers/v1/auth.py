"""Auth endpoints."""

from fastapi import APIRouter, Response

from pwstorage.core.dependencies.app import (
    AppConfigDependency,
    ClientHostDependency,
    RedisDependency,
    RefreshTokenDependency,
    SessionDependency,
    TokenDataDependency,
    UserAgentDependency,
)
from pwstorage.core.exceptions.auth import BadAuthDataException, BadFingerprintException
from pwstorage.lib.db import auth as auth_db, auth_session as auth_session_db
from pwstorage.lib.schemas.auth import TokenCreateSchema, TokenRefreshSchema, TokenSchema
from pwstorage.lib.utils.openapi import exc_list


router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login", openapi_extra=exc_list(BadAuthDataException))
async def login(
    response: Response,
    config: AppConfigDependency,
    db: SessionDependency,
    redis: RedisDependency,
    user_agent: UserAgentDependency,
    client_host: ClientHostDependency,
    schema: TokenCreateSchema,
) -> TokenSchema:
    """Login."""
    result = await auth_db.create_token(config.jwt, db, redis, client_host, user_agent, schema)
    response.set_cookie("refresh_token", result.refresh_token, max_age=result.refresh_token_expires_in * 60)
    return result


@router.post("/refresh_tokens", openapi_extra=exc_list(BadFingerprintException))
async def refresh_tokens(
    response: Response,
    config: AppConfigDependency,
    db: SessionDependency,
    redis: RedisDependency,
    user_agent: UserAgentDependency,
    client_host: ClientHostDependency,
    refresh_token: RefreshTokenDependency,
    schema: TokenRefreshSchema,
) -> TokenSchema:
    """Refresh tokens."""
    result = await auth_db.refresh_token(config.jwt, db, redis, client_host, user_agent, refresh_token, schema)
    response.set_cookie("refresh_token", result.refresh_token, max_age=result.refresh_token_expires_in * 60)
    return result


@router.delete("/logout")
async def logout(
    response: Response,
    db: SessionDependency,
    redis: RedisDependency,
    user_agent: UserAgentDependency,
    client_host: ClientHostDependency,
    token_data: TokenDataDependency,
) -> None:
    """Logout."""
    response.delete_cookie("refresh_token")
    return await auth_session_db.delete_session(db, redis, client_host, user_agent, token_data.session_id)
