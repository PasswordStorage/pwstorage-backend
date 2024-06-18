"""SettingsModel CRUD."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from pwstorage.lib.models import SettingsModel
from pwstorage.lib.schemas.settings import SettingsPatchSchema, SettingsSchema, SettingsUpdateSchema


async def get_settings_model(db: AsyncSession, user_id: int) -> SettingsModel:
    """Get a settings model.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID.

    Returns:
        SettingsModel: SettingsModel object.
    """
    query = select(SettingsModel).where(SettingsModel.user_id == user_id)
    return (await db.execute(query)).scalar_one()


async def create_settings(db: AsyncSession, user_id: int) -> SettingsSchema:
    """Create settings."""
    record_model = SettingsModel(user_id=user_id)
    db.add(record_model)

    await db.flush()
    return SettingsSchema.model_construct(**record_model.to_dict())


async def get_settings(db: AsyncSession, user_id: int) -> SettingsSchema:
    """Get settings."""
    settings_model = await get_settings_model(db, user_id)
    return SettingsSchema.model_construct(**settings_model.to_dict())


async def update_settings(
    db: AsyncSession, user_id: int, schema: SettingsUpdateSchema | SettingsPatchSchema
) -> SettingsSchema:
    """Update settings."""
    settings_model = await get_settings_model(db, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(settings_model, field, value)

    await db.flush()
    return SettingsSchema.model_construct(**settings_model.to_dict())


async def delete_settings(db: AsyncSession, user_id: int) -> None:
    """Delete settings."""
    await db.execute(delete(SettingsModel).where(SettingsModel.user_id == user_id))
