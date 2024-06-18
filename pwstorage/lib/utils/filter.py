"""Filtration utilities."""

from logging import getLogger
from typing import Any, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute

from pwstorage.core.exceptions.filter import FilterGroupAlreadyInUseException
from pwstorage.lib.models.abc import AbstractModel
from pwstorage.lib.schemas.abc import BaseSchema
from pwstorage.lib.schemas.enums.filter import FilterType, OrderByType


logger = getLogger(__name__)

_SelectType = TypeVar("_SelectType", bound=Any)


def add_filters_to_query(
    query: Select[_SelectType], table: type[AbstractModel], body: BaseSchema, *, include_order_by: bool = True
) -> Select[_SelectType]:
    """Add filter to query.

    Args:
        query (GenerativeSelect): Query to filter.
        id_column (InstrumentedAttribute[int]): ID column. Needed for ordering.
        body (Any): Filter body.
        include_order_by (bool): Include order by filder.

    Returns:
        GenerativeSelect: Filtered query.
    """
    groups: set[str] = set()

    for field_name, field in body.model_fields.items():
        field_value = getattr(body, field_name)
        if field_value is None:
            continue
        extra: dict[str, Any]
        if callable(field.json_schema_extra):
            logger.warn(
                "Filter schema extra for field %s.%s is not a dict, but a callable", body.__class__.__name__, field_name
            )
            continue
        if field.json_schema_extra is not None:
            extra = field.json_schema_extra
        else:
            if hasattr(field, "_inititial_kwargs"):
                extra = field._inititial_kwargs
            else:
                extra = {}
        table_column = extra.get("table_column", field_name)
        filter_type = extra.get("filter_type", FilterType.eq)
        # Check if filter group is already in use, if set
        filter_group = extra.get("group", None)
        if filter_group is not None:
            if filter_group in groups:
                raise FilterGroupAlreadyInUseException(group=filter_group)
            groups.add(filter_group)
        # Skip filters
        if filter_type == FilterType.skip:
            logger.debug("Skipping filter by %s with %s and %s", table_column, filter_type, field_value)
            continue

        logger.debug("Filtering by %s with %s and %s", table_column, filter_type, field_value)
        # Replace special characters for LIKE and ILIKE filters
        # and add % to the beginning and the end of the string
        # to make it work like a wildcard
        # https://www.postgresql.org/docs/current/functions-matching.html
        if filter_type in (FilterType.like, FilterType.ilike):
            field_value = field_value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_").replace("~", "\\~")
            field_value = field_value + "%"
        # Get column object
        table_column_obj: InstrumentedAttribute[Any] | None = getattr(table, table_column, None)
        if table_column_obj is None:
            raise ValueError("Table %s has no column %s", table, table_column)
        # Add filter to query
        match filter_type:
            case FilterType.eq:
                query = query.filter(table_column_obj == field_value)
            case FilterType.ne:
                query = query.filter(table_column_obj != field_value)
            case FilterType.gt:
                query = query.filter(table_column_obj > field_value)
            case FilterType.ge:
                query = query.filter(table_column_obj >= field_value)
            case FilterType.lt:
                query = query.filter(table_column_obj < field_value)
            case FilterType.le:
                query = query.filter(table_column_obj <= field_value)
            case FilterType.like:
                query = query.filter(table_column_obj.like(field_value))
            case FilterType.ilike:
                query = query.filter(table_column_obj.ilike(field_value))
            case FilterType.order_by:
                if include_order_by:
                    query = query.order_by(
                        table_column_obj.asc() if field_value == OrderByType.ASC else table_column_obj.desc()
                    )
            case FilterType.func:
                func = extra.get("filter_func")
                if func is None:
                    raise ValueError("Filter function is not defined")
                query = func(query, table_column_obj, field_value)
            case _:
                raise NotImplementedError

    logger.debug("Filtered query: %s", query)

    return query
