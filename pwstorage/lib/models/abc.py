"""Base classes for database models."""

import typing as t

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


_T = t.TypeVar("_T", bound="AbstractModel")


class AbstractModel(DeclarativeBase):
    """Base database model.

    It provides the basic methods like save, remove, update, etc.
    for all the models.

    Models with one primary key are supported.
    """

    __abstract__ = True

    def __repr__(self) -> str:
        """Return the representation of the model."""
        _repr = f"<{self.__class__.__name__} "
        for name in self._get_primary_keys():
            _repr += f"{name}={self._get_key_value(name)}, "
        return _repr[:-2] + ">"

    def __str__(self) -> str:
        """Return the string representation of the model."""
        return self.__repr__()

    def to_dict(self) -> dict[str, t.Any]:
        """Return the dictionary representation of the model."""
        return self.__dict__

    @classmethod
    def from_dict(cls: t.Type[_T], data: dict[str, t.Any]) -> _T:
        """Create a model from a dictionary."""
        return cls(**data)

    @classmethod
    def from_schema(cls: t.Type[_T], model: BaseModel) -> _T:
        """Create a model from pydantic schema."""
        return cls.from_dict(model.model_dump())

    @classmethod
    def _get_primary_keys(cls) -> list[str]:
        """Return the primary keys of the model."""
        return [i.name for i in cls.__table__.primary_key.columns.values()]  # type: ignore

    def _get_key_value(self, name: str) -> t.Any:
        """Return the primary key value of the model."""
        return getattr(self, name)
