"""User schemas."""

from datetime import datetime
from typing import Annotated

from . import fields as f, validators as v
from .abc import BaseSchema


USER_EMAIL = f.BaseField(description="User email.", min_length=3, max_length=128, examples=["anonymous@gmail.com"])
USER_NAME = f.BaseField(description="User name.", min_length=3, max_length=64, examples=["Anonymous"])
USER_PASSWORD = f.BaseField(description="User password.", min_length=6, max_length=128, examples=["P@$sW0rd!"])
USER_CREATED_AT = f.DATETIME(prefix="User creation datetime.")
USER_DELETED_AT = f.DATETIME(prefix="User deletion datetime.")

UserEmail = Annotated[str, v.python_regex(r"^[-\w\.]+@([\w-]+\.)+[\w-]{2,4}$")]
UserName = Annotated[str, v.python_regex(r"^[\da-zA-Z-_]+$")]
UserPassword = Annotated[str, v.python_regex(r"^[A-Za-z\d@$!%*?&]+$")]


class BaseUserSchema(BaseSchema):
    """Base user schema."""

    email: UserEmail = USER_EMAIL
    name: UserName = USER_NAME


class UserCreateSchema(BaseUserSchema):
    """Create user schema."""

    password: UserPassword = USER_PASSWORD


class UserUpdateSchema(BaseUserSchema):
    """Update user schema."""

    pass


class UserPatchSchema(UserUpdateSchema):
    """Patch user schema."""

    email: UserEmail = USER_EMAIL(default=None)
    name: UserName = USER_NAME(default=None)


class UserSchema(BaseUserSchema):
    """User schema."""

    created_at: datetime = USER_CREATED_AT
