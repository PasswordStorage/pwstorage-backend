"""Auth schemas."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from jwt import encode as jwt_encode

from . import fields as f, validators as v
from .abc import BaseSchema
from .user import USER_EMAIL, USER_PASSWORD, UserEmail, UserPassword


# Field definitions for Auth schemas
TOKEN = f.BaseField(
    description="JSON Web Token.",
    examples=[jwt_encode({"sub": str(uuid4()), "exp": datetime.now(timezone.utc)}, "SECRET_KEY")],
)
TOKEN_EXPIRATION = f.BaseField(description="Token expiration in minutes.", ge=5, le=525600, examples=[43800])
FINGERPRINT = f.BaseField(
    description="Fingerprint.", min_length=32, max_length=64, examples=["f1b7e156414663c4b81fbadadedcf01f"]
)

# Type alias for token fingerprint with validation
TokenFingerprint = Annotated[str, v.python_regex(r"^[\da-zA-Z]+$")]


class TokenRedisData(BaseSchema):
    """Token redis data.

    This schema represents the data stored in Redis for a token.
    """

    session_id: UUID
    user_id: int
    encryption_key: str


class TokenCreateSchema(BaseSchema):
    """Token create schema.

    This schema is used for creating a new token.
    """

    email: UserEmail = USER_EMAIL
    password: UserPassword = USER_PASSWORD
    fingerprint: TokenFingerprint = FINGERPRINT


class TokenRefreshSchema(BaseSchema):
    """Token refresh schema.

    This schema is used for refreshing an existing token.
    """

    fingerprint: TokenFingerprint = FINGERPRINT


class TokenSchema(BaseSchema):
    """Token schema.

    This schema represents a token with its details.
    """

    access_token: str = TOKEN
    refresh_token: str = TOKEN
    access_token_expires_in: int = TOKEN_EXPIRATION
    refresh_token_expires_in: int = TOKEN_EXPIRATION
