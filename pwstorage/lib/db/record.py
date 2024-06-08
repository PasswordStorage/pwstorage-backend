"""RecordModel CRUD."""

from typing import Sequence
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from pwstorage.core.exceptions.record import RecordNotFoundException
from pwstorage.core.security import Encryptor
from pwstorage.lib.models import RecordModel
from pwstorage.lib.schemas.pagination import PaginationRequest
from pwstorage.lib.schemas.record import (
    RecordCreateSchema,
    RecordFilterRequest,
    RecordPaginationResponse,
    RecordPatchSchema,
    RecordSchema,
    RecordUpdateSchema,
)
from pwstorage.lib.utils.filter import add_filters_to_query
from pwstorage.lib.utils.pagination import add_pagination_to_query, get_rows_count_in

from . import folder as folder_db


async def get_record_model(db: AsyncSession, record_id: int, user_id: int) -> RecordModel:
    """Get a record model.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        record_id (int): Record ID.
        user_id (int): User ID.

    Returns:
        RecordModel: RecordModel object.
    """
    query = select(RecordModel).where(RecordModel.id == record_id, RecordModel.owner_user_id == user_id)
    result = (await db.execute(query)).scalar_one_or_none()

    if result is None:
        raise RecordNotFoundException(record_id=record_id)

    return result


async def create_record(
    db: AsyncSession, encryptor: Encryptor, encryption_key: str, user_id: int, schema: RecordCreateSchema
) -> RecordSchema:
    """Create record."""
    if schema.folder_id is not None:
        await folder_db.raise_for_folder_exist(db, schema.folder_id, user_id)

    record_model = RecordModel(
        **schema.model_dump() | {"content": encryptor.encrypt_text(schema.content, encryption_key)},
        owner_user_id=user_id,
    )
    db.add(record_model)

    await db.flush()
    return RecordSchema.model_construct(**record_model.to_dict() | {"content": schema.content})


async def get_records(
    db: AsyncSession, user_id: int, pagination: PaginationRequest, filters: RecordFilterRequest
) -> RecordPaginationResponse:
    """Get records."""
    query = select(RecordModel).where(RecordModel.owner_user_id == user_id)
    query_count = select(func.count(RecordModel.id))

    query = add_filters_to_query(query, RecordModel, filters)
    query_count = add_filters_to_query(query_count, RecordModel, filters)
    query = add_pagination_to_query(query, RecordModel.id, pagination)

    result: Sequence[RecordModel] = (await db.execute(query)).scalars().all()
    schemas = [RecordSchema.model_construct(**record.to_dict() | {"content": None}) for record in result]

    count, pages = await get_rows_count_in(db, query_count, pagination.limit)

    return RecordPaginationResponse.model_construct(items=schemas, total_items=count, total_pages=pages)


async def get_record(
    db: AsyncSession, encryptor: Encryptor, encryption_key: str, record_id: int, user_id: int
) -> RecordSchema:
    """Get record."""
    record_model = await get_record_model(db, record_id, user_id)
    return RecordSchema.model_construct(
        **record_model.to_dict() | {"content": encryptor.decrypt_text(record_model.content, encryption_key)}
    )


async def update_record(
    db: AsyncSession,
    encryptor: Encryptor,
    encryption_key: str,
    record_id: int,
    user_id: int,
    schema: RecordUpdateSchema | RecordPatchSchema,
) -> RecordSchema:
    """Update record."""
    record_model = await get_record_model(db, record_id, user_id)

    if schema.folder_id is not None and schema.folder_id != record_model.folder_id:
        await folder_db.raise_for_folder_exist(db, schema.folder_id, user_id)

    if schema.content is not None:
        record_model.content = encryptor.encrypt_text(schema.content, encryption_key)

    for field, value in schema.iterate_set_fields(exclude=["content"]):
        setattr(record_model, field, value)

    record_model.updated_at = datetime.now(timezone.utc)

    await db.flush()
    return RecordSchema.model_construct(
        **record_model.to_dict() | {"content": encryptor.decrypt_text(record_model.content, encryption_key)}
    )


async def delete_record(db: AsyncSession, record_id: int, user_id: int) -> None:
    """Delete record."""
    record_model = await get_record_model(db, record_id, user_id)
    await db.delete(record_model)


async def delete_user_foldes(db: AsyncSession, user_id: int) -> None:
    """Delete user records."""
    await db.execute(delete(RecordModel).where(RecordModel.owner_user_id == user_id))
