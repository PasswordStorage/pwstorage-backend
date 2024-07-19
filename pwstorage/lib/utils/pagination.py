"""Pagination utilities."""

from typing import Any, TypeVar

from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from pwstorage.lib.schemas.pagination import PaginationRequest


_SelectType = TypeVar("_SelectType", bound=Any)


def add_pagination_to_query(query: Select[_SelectType], body: PaginationRequest) -> Select[_SelectType]:
    """Add pagination to a SQLAlchemy query.

    Args:
        query (Select[_SelectType]): The query to paginate.
        body (PaginationRequest): The pagination request body.

    Returns:
        Select[_SelectType]: The paginated query.
    """
    return query.slice((body.page - 1) * body.limit, body.page * body.limit)


async def get_rows_count_in(
    db: AsyncSession, id_column: InstrumentedAttribute[Any] | Select[Any], limit: int
) -> tuple[int, int]:
    """Get the count of rows and the number of pages in a table.

    Args:
        db (AsyncSession): The async SQLAlchemy session.
        id_column (InstrumentedAttribute[int] | Select[Any]): The ID column or a query to count rows.
        limit (int): The limit of items per page.

    Returns:
        tuple[int, int]: The count of rows and the number of pages.
    """
    if isinstance(id_column, Select):
        # If id_column is a query, execute it and get the result
        res = (await db.execute(id_column)).scalar()
    else:
        # Otherwise, construct a query to count the rows
        res = (await db.execute(func.count(id_column))).scalar()

    if not isinstance(res, int):
        raise TypeError("Rows count is not an integer")

    pages = res / limit
    if pages % 1 != 0:
        pages = int(pages) + 1

    return res, int(pages)
