"""Settings schemas."""

from . import fields as f
from .abc import BaseSchema


# Field definition for auth session expiration
AUTH_SESSION_EXPIRATION = f.BaseField(description="Auth session expires in minutes.", ge=1, le=525600, examples=[43800])


class BaseSettingsSchema(BaseSchema):
    """Base settings schema.

    This class serves as a base for other settings-related schemas, providing common fields and configurations.
    """

    auth_session_expiration: int = AUTH_SESSION_EXPIRATION


class SettingsUpdateSchema(BaseSettingsSchema):
    """Update settings schema.

    This schema is used for updating settings.
    """


class SettingsPatchSchema(SettingsUpdateSchema):
    """Patch settings schema.

    This schema is used for partially updating settings.
    """

    auth_session_expiration: int = AUTH_SESSION_EXPIRATION(default=None)


class SettingsSchema(BaseSettingsSchema):
    """Settings schema.

    This schema represents the settings with their details.
    """
