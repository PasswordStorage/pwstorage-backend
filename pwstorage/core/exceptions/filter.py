"""Filter exceptions."""

from .abc import AbstractException, ConflictException


class FilterException(AbstractException):
    """Filter exception."""


class FilterGroupAlreadyInUseException(FilterException, ConflictException):
    """Filter group already in use."""

    detail = "Cannot use the same filter from the same group ({group}) more than once"
