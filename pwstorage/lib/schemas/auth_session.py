"""Auth session schemas."""

from datetime import datetime
from typing import Sequence
from uuid import UUID

from . import fields as f
from .abc import BaseSchema
from .pagination import PaginationResponse


AUTH_SESSION_ID = f.UUID(prefix="Auth session ID.")
AUTH_SESSION_EXPIRES_IN = f.BaseField(description="Auth session expires in minutes.", examples=[43800])
AUTH_SESSION_LAST_ONLINE_AT = f.DATETIME(prefix="Auth session last online datetime.")
AUTH_SESSION_CREATED_AT = f.DATETIME(prefix="Auth session creation datetime.")
USER_IP = f.BaseField(description="User IP.", examples=["127.0.0.1"])
USER_AGENT = f.BaseField(description="User agent.", examples=["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"])


class BaseAuthSessionSchema(BaseSchema):
    """Base auth session schema."""

    user_ip: str = USER_IP
    user_agent: str | None = USER_AGENT
    expires_in: int = AUTH_SESSION_EXPIRES_IN


class AuthSessionSchema(BaseAuthSessionSchema):
    """auth session schema."""

    id: UUID = AUTH_SESSION_ID
    last_online: datetime = AUTH_SESSION_LAST_ONLINE_AT
    created_at: datetime = AUTH_SESSION_CREATED_AT


class AuthSessionPaginationResponse(PaginationResponse[AuthSessionSchema]):
    """AuthSession pagination response schema."""

    items: Sequence[AuthSessionSchema]
