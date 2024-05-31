"""Common exceptions for the API."""

from .abc import InternalServerErrorException


class DatabaseException(InternalServerErrorException):
    """Exception raises when a database error occurs."""


class CacheException(InternalServerErrorException):
    """Exception raises when a cache error occurs."""
