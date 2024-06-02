"""Auth schemas."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from jwt import encode as jwt_encode

from . import fields as f, validators as v
from .abc import BaseSchema
from .user import USER_EMAIL, USER_PASSWORD, UserEmail, UserPassword


TOKEN = f.BaseField(
    description="JSON Web Token.",
    examples=[jwt_encode({"sub": str(uuid4()), "exp": datetime.now(timezone.utc)}, "SECRET_KEY")],
)
TOKEN_EXPIRATION = f.BaseField(description="Token expiration in minutes.", ge=5, le=525600, examples=[43800])
FINGERPRINT = f.BaseField(
    description="Fingerprint.", min_length=32, max_length=64, examples=["f1b7e156414663c4b81fbadadedcf01f"]
)

TokenFingerprint = Annotated[str, v.python_regex(r"^[\da-zA-Z-]{32,64}$")]


class TokenData(BaseSchema):
    """Token redis data."""

    session_id: UUID
    user_id: int


class TokenCreateSchema(BaseSchema):
    """Token create schema."""

    email: UserEmail = USER_EMAIL
    password: UserPassword = USER_PASSWORD
    fingerprint: TokenFingerprint = FINGERPRINT
    expires_in: int = TOKEN_EXPIRATION(default=43800)


class TokenRefreshSchema(BaseSchema):
    """Token refresh schema."""

    fingerprint: TokenFingerprint = FINGERPRINT


class TokenSchema(BaseSchema):
    """Token create schema."""

    access_token: str = TOKEN
    refresh_token: str = TOKEN
    access_token_expires_in: int = TOKEN_EXPIRATION
    refresh_token_expires_in: int = TOKEN_EXPIRATION
