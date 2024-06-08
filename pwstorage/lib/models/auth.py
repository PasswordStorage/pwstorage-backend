"""Auth session model."""

from datetime import datetime, timezone
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid as SqlUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel
from .user import UserModel


class AuthSessionModel(AbstractModel):
    """Auth session model."""

    __tablename__ = "auth_sessions"

    id: Mapped[PyUUID] = mapped_column("id", SqlUUID(native_uuid=True, as_uuid=True), primary_key=True, default=uuid4)
    """Auth session ID."""

    user_id: Mapped[int] = mapped_column("user_id", ForeignKey("users.id"), nullable=False)
    """User ID.

    This is a foreign key to the user table.
    """

    user_ip: Mapped[str] = mapped_column("user_ip", String(128), nullable=False)
    """Auth session user ip."""

    user_agent: Mapped[str | None] = mapped_column("user_agent", String(256), nullable=True)
    """Auth session user agent."""

    fingerprint: Mapped[str] = mapped_column("fingerprint", String(128), nullable=False)
    """Auth session fingerprint."""

    access_token: Mapped[PyUUID | None] = mapped_column(
        "access_token", SqlUUID(native_uuid=True, as_uuid=True), nullable=True, unique=True, default=uuid4
    )
    """Auth session access token."""

    refresh_token: Mapped[PyUUID | None] = mapped_column(
        "refresh_token", SqlUUID(native_uuid=True, as_uuid=True), nullable=True, unique=True, default=uuid4
    )
    """Auth session refresh token."""

    expires_in: Mapped[int] = mapped_column("expires_in", Integer(), nullable=False)
    """Auth session expiration in minutes."""

    last_online: Mapped[datetime] = mapped_column(
        "last_online", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    """Auth session last online timestamp."""

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    """Auth session creation timestamp."""

    deleted_at: Mapped[datetime | None] = mapped_column("deleted_at", DateTime(timezone=True), nullable=True)
    """Auth session deletion timestamp."""

    user: Mapped[UserModel] = relationship("UserModel")
    """User model.

    This is a relationship to the user model. This is a many-to-one relationship.
    """
