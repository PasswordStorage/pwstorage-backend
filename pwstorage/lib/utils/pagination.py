"""Pagination utilities."""

from typing import Any, TypeVar

from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from pwstorage.lib.schemas.pagination import PaginationRequest


_SelectType = TypeVar("_SelectType", bound=Any)


def add_pagination_to_query(
    query: Select[_SelectType], id_column: InstrumentedAttribute[Any], body: PaginationRequest
) -> Select[_SelectType]:
    """Add pagination to query.

    Args:
        query (GenerativeSelect): Query to paginate.
        id_column (InstrumentedAttribute[int]): ID column. Needed for ordering.
        body (PaginationRequest): Pagination body.

    Returns:
        GenerativeSelect: Paginated query.
    """
    return query.order_by(id_column).slice((body.page - 1) * body.limit, body.page * body.limit)


async def get_rows_count_in(
    db: AsyncSession, id_column: InstrumentedAttribute[Any] | Select[Any], limit: int
) -> tuple[int, int]:
    """Get rows count in table.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        id_column (InstrumentedAttribute[int]): ID column.
        limit (int): Limit.

    Returns:
        tuple[int, int]: Rows count and pages count.
    """
    if isinstance(id_column, Select):
        # If id_column is a query, then execute it and get the result
        res = (await db.execute(id_column)).scalar()
    else:
        # Else, construct a query and count the rows
        res = (await db.execute(func.count(id_column))).scalar()
    if not isinstance(res, int):
        raise TypeError("Rows count is not an integer")
    pages = res / limit
    if pages % 1 != 0:
        pages = int(pages) + 1
    return res, int(pages)
