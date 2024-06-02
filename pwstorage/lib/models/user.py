"""User model."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .abc import AbstractModel


class UserModel(AbstractModel):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    """User ID."""

    email: Mapped[str] = mapped_column("email", String(256), nullable=False, index=True)
    """User email."""

    password_hash: Mapped[str] = mapped_column("password_hash", String(128), nullable=False)
    """User password hash."""

    name: Mapped[str] = mapped_column("name", String(128), nullable=False)
    """User name."""

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    """User creation timestamp."""

    deleted_at: Mapped[datetime | None] = mapped_column("deleted_at", DateTime(timezone=True), nullable=True)
    """User deletion timestamp."""

    __table_args__ = (Index("idx_users_email", func.lower(email)),)
