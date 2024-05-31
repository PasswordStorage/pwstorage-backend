"""Inclusion filter."""

from typing import TYPE_CHECKING, Any, TypeVar


if TYPE_CHECKING:
    from sqlalchemy import Select
    from sqlalchemy.orm import InstrumentedAttribute

_SelectType = TypeVar("_SelectType", bound=Any)


def inclusion_filter(
    query: "Select[_SelectType]", column: "InstrumentedAttribute[Any]", value: bool
) -> "Select[_SelectType]":
    """Get query with inclusion filter.

    Args:
        query (GenerativeSelect): Query to filter.
        column (InstrumentedAttribute[Any]): Column for filter.
        value (bool): Inclusion type.
    """
    return query.filter(column.is_not(None) if value else column.is_(None))
