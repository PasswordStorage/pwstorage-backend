"""FolderModel CRUD."""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from pwstorage.core.exceptions.folder import FolderNotFoundException
from pwstorage.lib.models import FolderModel
from pwstorage.lib.schemas.folder import (
    FolderCreateSchema,
    FolderPaginationResponse,
    FolderPatchSchema,
    FolderSchema,
    FolderUpdateSchema,
)
from pwstorage.lib.schemas.pagination import PaginationRequest
from pwstorage.lib.utils.pagination import add_pagination_to_query, get_rows_count_in


async def raise_for_folder_exist(db: AsyncSession, folder_id: int, user_id: int) -> None:
    """Raise an exception if the folder does not exist or is deleted.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        folder_id (int): Folder ID.
        user_id (int): User ID.

    Raises:
        FolderNotFoundException: If the folder is not found.
    """
    await get_folder_model(db, folder_id, user_id)


async def get_folder_model(db: AsyncSession, folder_id: int, user_id: int) -> FolderModel:
    """Get a folder model.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        folder_id (int): Folder ID.
        user_id (int): User ID.

    Returns:
        FolderModel: FolderModel object.

    Raises:
        FolderNotFoundException: If the folder is not found.
    """
    query = select(FolderModel).where(FolderModel.id == folder_id, FolderModel.owner_user_id == user_id)
    result = (await db.execute(query)).scalar_one_or_none()

    if result is None:
        raise FolderNotFoundException(folder_id=folder_id)

    return result


async def create_folder(db: AsyncSession, user_id: int, schema: FolderCreateSchema) -> FolderSchema:
    """Create a new folder.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID.
        schema (FolderCreateSchema): Schema containing folder creation data.

    Returns:
        FolderSchema: The created FolderSchema object.
    """
    if schema.parent_folder_id is not None:
        await raise_for_folder_exist(db, schema.parent_folder_id, user_id)

    folder_model = FolderModel(**schema.model_dump(), owner_user_id=user_id)
    db.add(folder_model)

    await db.flush()
    return FolderSchema.model_construct(**folder_model.to_dict())


async def get_folders(db: AsyncSession, user_id: int, pagination: PaginationRequest) -> FolderPaginationResponse:
    """Get folders with pagination.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID.
        pagination (PaginationRequest): Pagination request.

    Returns:
        FolderPaginationResponse: The paginated response containing folders.
    """
    query_filter = (FolderModel.owner_user_id == user_id,)
    query = select(FolderModel).where(*query_filter)
    query_count = select(func.count(FolderModel.id).filter(*query_filter))
    query = add_pagination_to_query(query, pagination)

    folders = (await db.execute(query)).scalars().all()
    total_items, pages = await get_rows_count_in(db, query_count, pagination.limit)

    items = [FolderSchema.model_construct(**folder.to_dict()) for folder in folders]
    return FolderPaginationResponse.model_construct(total_items=total_items, total_pages=pages, items=items)


async def get_folder(db: AsyncSession, folder_id: int, user_id: int) -> FolderSchema:
    """Get a specific folder.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        folder_id (int): Folder ID.
        user_id (int): User ID.

    Returns:
        FolderSchema: The retrieved FolderSchema object.
    """
    folder_model = await get_folder_model(db, folder_id, user_id)
    return FolderSchema.model_construct(**folder_model.to_dict())


async def update_folder(
    db: AsyncSession, folder_id: int, user_id: int, schema: FolderUpdateSchema | FolderPatchSchema
) -> FolderSchema:
    """Update a folder.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        folder_id (int): Folder ID.
        user_id (int): User ID.
        schema (FolderUpdateSchema | FolderPatchSchema): Schema containing folder update data.

    Returns:
        FolderSchema: The updated FolderSchema object.
    """
    folder_model = await get_folder_model(db, folder_id, user_id)

    if schema.parent_folder_id is not None and schema.parent_folder_id != folder_model.parent_folder_id:
        await raise_for_folder_exist(db, schema.parent_folder_id, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(folder_model, field, value)

    await db.flush()
    return FolderSchema.model_construct(**folder_model.to_dict())


async def delete_folder(db: AsyncSession, folder_id: int, user_id: int) -> None:
    """Delete a folder.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        folder_id (int): Folder ID.
        user_id (int): User ID.
    """
    folder_model = await get_folder_model(db, folder_id, user_id)
    await db.delete(folder_model)


async def delete_all_folders(db: AsyncSession, user_id: int) -> None:
    """Delete all folders for a user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID.
    """
    await db.execute(delete(FolderModel).where(FolderModel.owner_user_id == user_id))
