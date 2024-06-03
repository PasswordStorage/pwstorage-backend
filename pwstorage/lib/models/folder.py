"""Folder model."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .abc import AbstractModel


class FolderModel(AbstractModel):
    """Folder model."""

    __tablename__ = "folders"

    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    """Folder ID."""

    owner_user_id: Mapped[int] = mapped_column("owner_user_id", ForeignKey("users.id"), nullable=False)
    """Owner user ID.

    This is a foreign key to the user table.
    """

    parent_folder_id: Mapped[int | None] = mapped_column(
        "parent_folder_id", ForeignKey("folders.id", ondelete="CASCADE"), nullable=True
    )
    """Parent folder ID.

    This is a foreign key to the folder table.
    """

    name: Mapped[str] = mapped_column("name", String(128), nullable=False)
    """Folder name."""

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    """Folder creation timestamp."""
