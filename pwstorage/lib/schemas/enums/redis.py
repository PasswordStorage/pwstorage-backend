"""Redis types."""

from .abc import BaseEnum


class BaseRedisKeyType(BaseEnum):
    """Redis key types."""

    @property
    def _prefix(self) -> str:
        raise NotImplementedError


class AuthRedisKeyType(BaseRedisKeyType):
    """Redis key types."""

    _prefix = "auth"

    access: str = f"{_prefix}:access:{{}}"
    """Key for access token."""
