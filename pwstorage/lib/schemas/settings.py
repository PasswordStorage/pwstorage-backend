"""Settings schemas."""

from . import fields as f
from .abc import BaseSchema


AUTH_SESSION_EXPIRATION = f.BaseField(description="Auth session expires in minutes.", ge=1, le=525600, examples=[43800])


class BaseSettingsSchema(BaseSchema):
    """Base settings schema."""

    auth_session_expiration: int = AUTH_SESSION_EXPIRATION


class SettingsUpdateSchema(BaseSettingsSchema):
    """Update settings schema."""

    pass


class SettingsPatchSchema(SettingsUpdateSchema):
    """Patch settings schema."""

    auth_session_expiration: int = AUTH_SESSION_EXPIRATION(default=None)


class SettingsSchema(BaseSettingsSchema):
    """Settings schema."""

    pass
