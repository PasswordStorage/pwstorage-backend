"""Auth-related exceptions."""

from .abc import AbstractException, UnauthorizedException


class AuthException(AbstractException):
    """Base auth exception."""


class BadAuthDataException(AuthException, UnauthorizedException):
    """Bad auth data."""

    detail = "Bad auth data"


class BadFingerprintException(AuthException, UnauthorizedException):
    """Bad fingerprint."""

    detail = "Bad fingerprint"
