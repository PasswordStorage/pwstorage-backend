"""Folder schemas."""

from datetime import datetime
from typing import Annotated, Sequence

from . import fields as f, validators as v
from .abc import BaseSchema
from .pagination import PaginationResponse


FOLDER_ID = f.ID(prefix="Folder ID.")
FOLDER_PARENT_ID = f.ID(prefix="Folder parent ID.", examples=[None])
FOLDER_NAME = f.BaseField(description="Folder name.", min_length=1, max_length=64, examples=["MyFolder"])
FOLDER_CREATED_AT = f.DATETIME(prefix="Folder creation datetime.")

FolderName = Annotated[str, v.python_regex(r"^[\da-zA-Z-_]{1,64}$")]


class BaseFolderSchema(BaseSchema):
    """Base folder schema."""

    name: FolderName = FOLDER_NAME
    parent_folder_id: int | None = FOLDER_PARENT_ID


class FolderCreateSchema(BaseFolderSchema):
    """Create folder schema."""

    pass


class FolderUpdateSchema(FolderCreateSchema):
    """Update folder schema."""

    pass


class FolderPatchSchema(FolderUpdateSchema):
    """Patch folder schema."""

    name: FolderName = FOLDER_NAME(default=None)
    parent_folder_id: int | None = FOLDER_PARENT_ID(default=None)


class FolderSchema(BaseFolderSchema):
    """Folder schema."""

    id: int = FOLDER_ID
    created_at: datetime = FOLDER_CREATED_AT


class FolderPaginationResponse(PaginationResponse[FolderSchema]):
    """Folder pagination response schema."""

    items: Sequence[FolderSchema]
