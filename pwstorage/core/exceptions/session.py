"""AuthSession-related exceptions."""

from .abc import AbstractException, ConflictException, NotFoundException


class AuthSessionException(AbstractException):
    """Base auth session exception."""


class AuthSessionNotFoundException(AuthSessionException, NotFoundException):
    """Auth session not found."""

    detail = "Auth session not found"


class AuthSessionDeletedException(AuthSessionException, ConflictException):
    """Auth session deleted."""

    detail = "Auth session deleted"
