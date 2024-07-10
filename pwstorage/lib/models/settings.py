"""Settings model."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .user import UserModel


class SettingsModel(AbstractModel):
    """Settings model."""

    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column("user_id", ForeignKey("users.id"), primary_key=True)
    """User ID.

    This is a foreign key to the user table.
    """

    auth_session_expiration: Mapped[int] = mapped_column(
        "auth_session_expiration", Integer(), nullable=False, default=43800
    )
    """Auth session expiration in minutes."""

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="settings")
    """User model.

    This is a relationship to the user model. This is a one-to-one relationship.
    """
