"""Folder endpoints."""

from fastapi import APIRouter
from pyfa_converter_v2 import QueryDepends

from pwstorage.core.dependencies.app import SessionDependency, TokenDataDependency
from pwstorage.core.exceptions.folder import FolderNotFoundException
from pwstorage.lib.db import folder as folder_db
from pwstorage.lib.schemas.folder import (
    FolderCreateSchema,
    FolderPaginationResponse,
    FolderPatchSchema,
    FolderSchema,
    FolderUpdateSchema,
)
from pwstorage.lib.schemas.pagination import PaginationRequest
from pwstorage.lib.utils.openapi import exc_list


router = APIRouter(tags=["folder"], prefix="/folders")


@router.post("/", response_model=FolderSchema, openapi_extra=exc_list(FolderNotFoundException))
async def create_folder(
    db: SessionDependency, token_data: TokenDataDependency, schema: FolderCreateSchema
) -> FolderSchema:
    """Create folder."""
    return await folder_db.create_folder(db, token_data.user_id, schema)


@router.get("/", response_model=FolderPaginationResponse)
async def get_folders(
    db: SessionDependency,
    token_data: TokenDataDependency,
    pagination: PaginationRequest = QueryDepends(PaginationRequest),
) -> FolderPaginationResponse:
    """Get folders."""
    return await folder_db.get_folders(db, token_data.user_id, pagination)


@router.get("/{folder_id}", response_model=FolderSchema, openapi_extra=exc_list(FolderNotFoundException))
async def get_folder(db: SessionDependency, token_data: TokenDataDependency, folder_id: int) -> FolderSchema:
    """Get folder."""
    return await folder_db.get_folder(db, folder_id, token_data.user_id)


@router.put("/{folder_id}", response_model=FolderSchema, openapi_extra=exc_list(FolderNotFoundException))
async def update_folder(
    db: SessionDependency, token_data: TokenDataDependency, folder_id: int, schema: FolderUpdateSchema
) -> FolderSchema:
    """Update folder."""
    return await folder_db.update_folder(db, folder_id, token_data.user_id, schema)


@router.patch("/{folder_id}", response_model=FolderSchema, openapi_extra=exc_list(FolderNotFoundException))
async def patch_folder(
    db: SessionDependency, token_data: TokenDataDependency, folder_id: int, schema: FolderPatchSchema
) -> FolderSchema:
    """Patch folder."""
    return await folder_db.update_folder(db, folder_id, token_data.user_id, schema)


@router.delete("/{folder_id}", status_code=204, openapi_extra=exc_list(FolderNotFoundException))
async def delete_folder(db: SessionDependency, token_data: TokenDataDependency, folder_id: int) -> None:
    """Delete folder."""
    return await folder_db.delete_folder(db, folder_id, token_data.user_id)
