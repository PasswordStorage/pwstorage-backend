"""Common schemas for the API."""

from .abc import BaseSchema


class OKSchema(BaseSchema):
    """OK schema."""

    ok: bool = True
