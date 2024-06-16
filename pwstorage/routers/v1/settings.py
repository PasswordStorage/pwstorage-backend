"""Settings endpoints."""

from fastapi import APIRouter

from pwstorage.core.dependencies.app import SessionDependency, TokenDataDependency
from pwstorage.lib.db import settings as setting_db
from pwstorage.lib.schemas.settings import SettingsPatchSchema, SettingsSchema, SettingsUpdateSchema


router = APIRouter(tags=["settings"], prefix="/settings")


@router.get("/", response_model=SettingsSchema)
async def get_settings(db: SessionDependency, token_data: TokenDataDependency) -> SettingsSchema:
    """Get settings."""
    return await setting_db.get_settings(db, token_data.user_id)


@router.put("/", response_model=SettingsSchema)
async def update_settings(
    db: SessionDependency, token_data: TokenDataDependency, schema: SettingsUpdateSchema
) -> SettingsSchema:
    """Update settings."""
    return await setting_db.update_settings(db, token_data.user_id, schema)


@router.patch("/", response_model=SettingsSchema)
async def patch_settings(
    db: SessionDependency, token_data: TokenDataDependency, schema: SettingsPatchSchema
) -> SettingsSchema:
    """Patch settings."""
    return await setting_db.update_settings(db, token_data.user_id, schema)
