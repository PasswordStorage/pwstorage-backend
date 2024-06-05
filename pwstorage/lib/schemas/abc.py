"""Abstract base classes for schemas."""

from abc import ABC
from typing import Any, Generator

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """Format string to camelCase."""
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseSchema(BaseModel, ABC):
    """Base schema."""

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    def iterate_set_fields(self, exclude: list[str] = []) -> Generator[tuple[str, Any], None, None]:
        """Iterate over set fields."""
        for field_name in self.model_fields_set:
            if field_name in exclude:
                continue
            attr = getattr(self, field_name)
            yield field_name, attr
