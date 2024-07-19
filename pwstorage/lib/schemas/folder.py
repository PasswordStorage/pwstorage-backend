"""Folder schemas."""

from datetime import datetime
from typing import Annotated, Sequence

from . import fields as f, validators as v
from .abc import BaseSchema
from .pagination import PaginationResponse


# Field definitions for Folder schemas
FOLDER_ID = f.ID(prefix="Folder ID.")
FOLDER_PARENT_ID = f.ID(prefix="Folder parent ID.", examples=[None])
FOLDER_NAME = f.BaseField(description="Folder name.", min_length=1, max_length=64, examples=["MyFolder"])
FOLDER_CREATED_AT = f.DATETIME(prefix="Folder creation datetime.")

# Type alias for folder name with validation
FolderName = Annotated[str, v.CheckTextValidator]


class BaseFolderSchema(BaseSchema):
    """Base folder schema.

    This class serves as a base for other folder-related schemas, providing common fields and configurations.
    """

    name: FolderName = FOLDER_NAME
    parent_folder_id: int | None = FOLDER_PARENT_ID


class FolderCreateSchema(BaseFolderSchema):
    """Folder create schema.

    This schema is used for creating a new folder.
    """


class FolderUpdateSchema(FolderCreateSchema):
    """Update folder schema.

    This schema is used for updating an existing folder.
    """


class FolderPatchSchema(FolderUpdateSchema):
    """Patch folder schema.

    This schema is used for partially updating an existing folder.
    """

    name: FolderName = FOLDER_NAME(default=None)
    parent_folder_id: int | None = FOLDER_PARENT_ID(default=None)


class FolderSchema(BaseFolderSchema):
    """Folder schema.

    This schema represents a folder with additional metadata.
    """

    id: int = FOLDER_ID
    created_at: datetime = FOLDER_CREATED_AT


class FolderPaginationResponse(PaginationResponse[FolderSchema]):
    """Folder pagination response schema.

    This schema is used for paginated responses containing multiple folders.
    """

    items: Sequence[FolderSchema]
