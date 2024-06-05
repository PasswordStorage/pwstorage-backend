"""Ping endpoint."""

from fastapi import APIRouter

from pwstorage.lib.schemas.common import OKSchema


router = APIRouter(tags=["ping"], prefix="/ping")


@router.get("/", response_model=OKSchema)
async def ping() -> OKSchema:
    """Ping."""
    return OKSchema()
