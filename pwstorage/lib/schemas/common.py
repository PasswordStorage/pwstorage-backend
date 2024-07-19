"""Common schemas for the API."""

from .abc import BaseSchema


class OKSchema(BaseSchema):
    """OK schema.

    This schema represents a simple response indicating a successful operation.
    """

    ok: bool = True
