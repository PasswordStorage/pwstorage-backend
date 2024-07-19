"""Inclusion filter."""

from typing import Any, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute


_SelectType = TypeVar("_SelectType", bound=Any)


def inclusion_filter(
    query: Select[_SelectType], column: InstrumentedAttribute[Any], value: bool
) -> Select[_SelectType]:
    """Apply an inclusion filter to a SQLAlchemy query.

    Args:
        query (Select[_SelectType]): The query to filter.
        column (InstrumentedAttribute[Any]): The column to apply the filter on.
        value (bool): The inclusion type. If True, filter for non-null values; if False, filter for null values.

    Returns:
        Select[_SelectType]: The filtered query.
    """
    return query.filter(column.is_not(None) if value else column.is_(None))
