"""Record types."""

from .abc import BaseEnum


class RecordType(BaseEnum):
    """Record type."""

    note = "note"
    """Note."""
    login = "login"
    """Login."""
    card = "card"
    """Card."""
