"""Record model."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from pwstorage.lib.schemas.enums.record import RecordType

from .abc import AbstractModel


class RecordModel(AbstractModel):
    """Record model."""

    __tablename__ = "records"

    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    """Record ID."""

    owner_user_id: Mapped[int] = mapped_column("owner_user_id", ForeignKey("users.id"), nullable=False)
    """Owner user ID.

    This is a foreign key to the user table.
    """

    folder_id: Mapped[int | None] = mapped_column(
        "folder_id", ForeignKey("folders.id", ondelete="CASCADE"), nullable=True
    )
    """Folder ID.

    This is a foreign key to the folder table.
    """

    record_type: Mapped[RecordType] = mapped_column("record_type", Enum(RecordType), nullable=False)
    """Record type.."""

    title: Mapped[str] = mapped_column("title", String(128), nullable=False)
    """Record title."""

    content: Mapped[str] = mapped_column("content", String(), nullable=False)
    """Record content."""

    is_favorite: Mapped[bool] = mapped_column("is_favorite", Boolean(), nullable=False, default=False)
    """Record favorite status."""

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    """Record creation timestamp."""

    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    """Record updation timestamp."""
