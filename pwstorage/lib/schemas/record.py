"""Record schemas."""

from datetime import datetime
from typing import Annotated, Sequence

from . import fields as f, validators as v
from .abc import BaseSchema
from .enums.filter import FilterType, OrderByType
from .enums.record import RecordType
from .folder import FOLDER_ID
from .pagination import PaginationResponse


# Field definitions for Record schemas
RECORD_ID = f.ID(prefix="Record ID.")
RECORD_TYPE = f.BaseField(description="Record type.", examples=[RecordType.login])
RECORD_TITLE = f.BaseField(description="Record title.", min_length=1, max_length=128, examples=["MyRecord"])
RECORD_CONTENT = f.BaseField(description="Record content.", min_length=1, max_length=8192)
RECORD_IS_FAVORITE = f.BaseField(description="Record favorite status.", examples=[False])
RECORD_CREATED_AT = f.DATETIME(prefix="Record creation datetime.")
RECORD_UPDATED_AT = f.DATETIME(prefix="Record updation datetime.")

# Type alias for record title with validation
RecordTitle = Annotated[str, v.CheckTextValidator]


class BaseRecordSchema(BaseSchema):
    """Base record schema.

    This class serves as a base for other record-related schemas, providing common fields and configurations.
    """

    folder_id: int | None = FOLDER_ID
    title: RecordTitle = RECORD_TITLE
    is_favorite: bool = RECORD_IS_FAVORITE


class RecordCreateSchema(BaseRecordSchema):
    """Create record schema.

    This schema is used for creating a new record.
    """

    record_type: RecordType = RECORD_TYPE
    content: str = RECORD_CONTENT


class RecordUpdateSchema(BaseRecordSchema):
    """Update record schema.

    This schema is used for updating an existing record.
    """

    content: str = RECORD_CONTENT


class RecordPatchSchema(RecordUpdateSchema):
    """Patch record schema.

    This schema is used for partially updating an existing record.
    """

    folder_id: int | None = FOLDER_ID(default=None)
    title: RecordTitle = RECORD_TITLE(default=None)
    content: str = RECORD_CONTENT(default=None)
    is_favorite: bool = RECORD_IS_FAVORITE(default=None)


class RecordSchema(BaseRecordSchema):
    """Record schema.

    This schema represents a record with additional metadata.
    """

    id: int = RECORD_ID
    content: str | None = RECORD_CONTENT
    record_type: RecordType = RECORD_TYPE
    created_at: datetime = RECORD_CREATED_AT
    updated_at: datetime = RECORD_UPDATED_AT


class RecordFilterRequest(BaseSchema):
    """Record filter request schema.

    This schema is used for filtering records based on various criteria.
    """

    folder_id_eq: int | None = FOLDER_ID(default=None, filter_type=FilterType.eq, table_column="folder_id")
    record_type_eq: RecordType | None = RECORD_TYPE(default=None, filter_type=FilterType.eq, table_column="record_type")

    title_order_by: OrderByType | None = f.ORDER_BY_FILTER(table_column="title")
    created_at_order_by: OrderByType | None = f.ORDER_BY_FILTER(table_column="created_at")
    updated_at_order_by: OrderByType | None = f.ORDER_BY_FILTER(table_column="updated_at")

    title_eq: str | None = RECORD_TITLE(default=None, filter_type=FilterType.eq, table_column="title")
    title_ilike: str | None = RECORD_TITLE(default=None, filter_type=FilterType.ilike, table_column="title")

    created_at_from: datetime | None = RECORD_CREATED_AT(
        default=None, filter_type=FilterType.ge, table_column="created_at"
    )
    created_at_to: datetime | None = RECORD_CREATED_AT(
        default=None, filter_type=FilterType.le, table_column="created_at"
    )

    updated_at_from: datetime | None = RECORD_UPDATED_AT(
        default=None, filter_type=FilterType.ge, table_column="updated_at"
    )
    updated_at_to: datetime | None = RECORD_UPDATED_AT(
        default=None, filter_type=FilterType.le, table_column="updated_at"
    )

    is_favorite: bool | None = RECORD_IS_FAVORITE(default=None)


class RecordPaginationResponse(PaginationResponse[RecordSchema]):
    """Record pagination response schema.

    This schema is used for paginated responses containing multiple records.
    """

    items: Sequence[RecordSchema]
