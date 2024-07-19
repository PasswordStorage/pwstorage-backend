"""Abstract base classes for schemas."""

from abc import ABC
from typing import Any, Generator

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """Convert a snake_case string to camelCase.

    Args:
        string (str): The snake_case string.

    Returns:
        str: The camelCase formatted string.
    """
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseSchema(BaseModel, ABC):
    """Base schema class with common configurations and methods.

    This class serves as a base for other schema classes, providing common configurations such as alias generation
    and methods for iterating over set fields.
    """

    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    def iterate_set_fields(self, exclude: list[str] = []) -> Generator[tuple[str, Any], None, None]:
        """Iterate over fields that have been set.

        Args:
            exclude (list[str], optional): List of field names to exclude from iteration. Defaults to [].

        Yields:
            Generator[tuple[str, Any], None, None]: A generator yielding tuples of field names and their values.
        """
        for field_name in self.model_fields_set:
            if field_name in exclude:
                continue
            attr = getattr(self, field_name)
            yield field_name, attr
