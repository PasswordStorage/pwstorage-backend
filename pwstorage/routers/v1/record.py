"""Record endpoints."""

from fastapi import APIRouter
from pyfa_converter_v2 import QueryDepends

from pwstorage.core.dependencies.app import EncryptorDependency, SessionDependency, TokenDataDependency
from pwstorage.core.exceptions.record import RecordNotFoundException
from pwstorage.lib.db import record as record_db
from pwstorage.lib.schemas.pagination import PaginationRequest
from pwstorage.lib.schemas.record import (
    RecordCreateSchema,
    RecordFilterRequest,
    RecordPaginationResponse,
    RecordPatchSchema,
    RecordSchema,
    RecordUpdateSchema,
)
from pwstorage.lib.utils.openapi import exc_list


router = APIRouter(tags=["record"], prefix="/records")


@router.post("/", response_model=RecordSchema, openapi_extra=exc_list(RecordNotFoundException))
async def create_record(
    db: SessionDependency,
    token_data: TokenDataDependency,
    encryptor: EncryptorDependency,
    schema: RecordCreateSchema,
) -> RecordSchema:
    """Create record."""
    return await record_db.create_record(db, encryptor, token_data.encryption_key, token_data.user_id, schema)


@router.get("/", response_model=RecordPaginationResponse)
async def get_records(
    db: SessionDependency,
    token_data: TokenDataDependency,
    pagination: PaginationRequest = QueryDepends(PaginationRequest),
    filter: RecordFilterRequest = QueryDepends(RecordFilterRequest),
) -> RecordPaginationResponse:
    """Get records."""
    return await record_db.get_records(db, token_data.user_id, pagination, filter)


@router.get("/{record_id}", response_model=RecordSchema, openapi_extra=exc_list(RecordNotFoundException))
async def get_record(
    db: SessionDependency, token_data: TokenDataDependency, encryptor: EncryptorDependency, record_id: int
) -> RecordSchema:
    """Get record."""
    return await record_db.get_record(db, encryptor, token_data.encryption_key, record_id, token_data.user_id)


@router.put("/{record_id}", response_model=RecordSchema, openapi_extra=exc_list(RecordNotFoundException))
async def update_record(
    db: SessionDependency,
    token_data: TokenDataDependency,
    encryptor: EncryptorDependency,
    record_id: int,
    schema: RecordUpdateSchema,
) -> RecordSchema:
    """Update record."""
    return await record_db.update_record(
        db, encryptor, token_data.encryption_key, record_id, token_data.user_id, schema
    )


@router.patch("/{record_id}", response_model=RecordSchema, openapi_extra=exc_list(RecordNotFoundException))
async def patch_record(
    db: SessionDependency,
    token_data: TokenDataDependency,
    encryptor: EncryptorDependency,
    record_id: int,
    schema: RecordPatchSchema,
) -> RecordSchema:
    """Patch record."""
    return await record_db.update_record(
        db, encryptor, token_data.encryption_key, record_id, token_data.user_id, schema
    )


@router.delete("/{record_id}", status_code=204, openapi_extra=exc_list(RecordNotFoundException))
async def delete_record(db: SessionDependency, token_data: TokenDataDependency, record_id: int) -> None:
    """Delete record."""
    return await record_db.delete_record(db, record_id, token_data.user_id)
