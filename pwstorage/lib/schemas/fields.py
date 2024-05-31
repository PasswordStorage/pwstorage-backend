"""Generic fields for FastAPI schemas and Pydantic models and utilities to work with them."""

from logging import getLogger
from typing import Any, Self, no_type_check

from fastapi import Path, Query
from pydantic.fields import Field, FieldInfo

from pwstorage.lib.utils.inclusion_filter import inclusion_filter

from .enums.filter import FilterType


logger = getLogger(__name__)


@no_type_check
def wrap_field(field_info: Any) -> Any:
    """Wrap a field to add a custom metadata.

    It allows to easily manage fields with custom metadata for FastAPI schemas and Pydantic models, without having to
    repeat the metadata. It is useful to avoid code duplication and to keep the metadata in a single place.

    You can use wrapped fields as usual, but you can also update the metadata with the `__call__` method, like this:
    >>> field = wrap_field(Field(description="My description"))
    >>> field(examples=["My example"])
    ... Field(..., description="My description", examples=["My example"])

    And you can also convert the field to another class, like this:
    >>> field = wrap_field(Field(description="My description"))
    >>> field.to_class(Query, examples=["My example"])
    ... Query(..., description="My description", examples=["My example"])

    This can be useful to use the same field in different contexts, for example, to use the same field in a Pydantic
    model and in a FastAPI schema.

    Under the hood, the function uses dark magic and disables typing, as it is impossible to implement a similar
    patching with typing.

    Args:
        field_info: FieldInfo (or subclass, like fastapi.Query) instance to wrap.

    Returns:
        Patched FieldInfo class.

    Raises:
        TypeError: If field_info is not an instance of pydantic.FieldInfo (or a subclass).

    Examples:
        >>> from pydantic import Field, BaseModel
        >>> from pwstorage.lib.schemas.fields import wrap_field
        >>>
        >>> TIMESTAMP = wrap_field(
        ...     Field(description="Timestamp in seconds since UNIX epoch.", examples=[1610000000], ge=0)
        ... )
        >>>
        >>> class MyModel(BaseModel):
        ...     # The field is initialized with the metadata from TIMESTAMP.
        ...     timestamp: int = TIMESTAMP
        ...
        >>> class PatchedModel(BaseModel):
        ...     # The field is initialized with the metadata from TIMESTAMP and updated with the new metadata.
        ...     created_at: int = TIMESTAMP(description="Creation timestamp in seconds since UNIX epoch.")
        ...
    """
    if not isinstance(field_info, FieldInfo):
        raise TypeError("field_info must be an instance of pydantic.FieldInfo (or a subclass)")
    if getattr(field_info, "__is_wrapped_field__", False):
        logger.warning(
            "Attempt to wrap a wrapped field. Ignoring and returning it back. This is probably a bug. Field: (%s) %s",
            field_info.__class__.__name__,
            field_info,
        )
        return field_info

    class WrappedField(field_info.__class__):  # type: ignore
        """Wrapped field.

        This class is used to easily patch the metadata of a field.

        Attributes:
            _inititial_kwargs: Initial keyword arguments.
        """

        __is_wrapped_field__ = True

        def _get_kwargs(self) -> dict[str, Any]:
            """Get the keyword arguments of the field.

            Returns:
                The keyword arguments of the field.
            """
            return object.__getattribute__(self, "_inititial_kwargs").copy()

        def __call__(self, **new_kwargs: Any) -> Any:
            """Get a new field with updated metadata.

            This method does not mutate object state, instead, it returns a new object.

            Args:
                **new_kwargs: Keyword arguments to update the metadata.

            Returns:
                A new field with updated metadata.
            """
            kwargs = self._get_kwargs()
            kwargs.update(new_kwargs)
            return self.__class__._init_wrapped(kwargs)

        @classmethod
        def _init_wrapped(cls, initial_kwargs: dict[str, Any]) -> Self:
            """Initialize the wrapped field.

            Args:
                initial_kwargs: Initial keyword arguments.

            Returns:
                The wrapped field.
            """
            suffix = initial_kwargs.pop("suffix", None)
            if suffix is not None:
                initial_kwargs["description"] = initial_kwargs.get("description", "") + " " + suffix

            prefix = initial_kwargs.pop("prefix", None)
            if prefix is not None:
                initial_kwargs["description"] = prefix + " " + initial_kwargs.get("description", "")

            if initial_kwargs.get("description") is not None:
                initial_kwargs["description"] = initial_kwargs["description"].strip()

            c = cls(**initial_kwargs)
            # Why we use object.__setattr__ instead of self._inititial_kwargs = initial_kwargs?
            # Because mypy raises an error about non-existing attribute.
            object.__setattr__(
                c, "_inititial_kwargs", initial_kwargs
            )  # store initial kwargs, so we can recreate the field
            object.__setattr__(c, "__doc__", initial_kwargs.get("description"))  # replace docstring
            return c

        def to_class(self, _class: Any, **new_kwargs: Any) -> Any:
            """Convert the field to another class.

            Args:
                _class: Class to convert the field to.
                **kwargs: Keyword arguments to pass to the class constructor.

            Returns:
                A new instance of the class. The field is initialized with the metadata from the wrapped field.
            """
            kwargs = self._get_kwargs()
            kwargs.update(new_kwargs)
            return wrap_field(_class(**kwargs))

        def to_path(self) -> Any:
            """Convert the field to a path.

            Returns:
                A new instance of the class. The field is initialized with the metadata from the wrapped field.
            """
            if hasattr(self, "_path_cache"):
                return self._path_cache
            kwargs = self._get_kwargs()
            kwargs.pop("default")
            path = Path(**kwargs)
            setattr(self, "_path_cache", path)
            return path

        def to_query(self) -> Any:
            """Convert the field to a query.

            Returns:
                A new instance of the class. The field is initialized with the metadata from the wrapped field.
            """
            if hasattr(self, "_query_cache"):
                return self._query_cache
            kwargs = self._get_kwargs()
            kwargs.pop("default")
            query = Query(**kwargs)
            setattr(self, "_query_cache", query)
            return query

        @property
        def path(self) -> Any:
            """Convert the field to a path.

            Returns:
                A new instance of the class. The field is initialized with the metadata from the wrapped field.
            """
            return self.to_path()

        @property
        def query(self) -> Any:
            """Convert the field to a query.

            Returns:
                A new instance of the class. The field is initialized with the metadata from the wrapped field.
            """
            return self.to_query()

    # Copy the name of the original field to the wrapped field.
    WrappedField.__name__ = "Wrapped" + field_info.__class__.__name__
    # Copy attributes from the original field to the wrapped field.
    dict_ = {}
    for attr in field_info.__slots__:
        dict_[attr] = getattr(field_info, attr)
    # Fix "extra" attribute.
    if "extra" in dict_:
        extra = dict_.pop("extra")
        if extra is not None:
            dict_.update(extra)
    # Initialize the wrapped field.
    return WrappedField._init_wrapped(dict_)


# Common fields.
# Regexes are taken from https://ihateregex.io/
BaseField = wrap_field(Field())
"""Base field.

It is used to create other fields and remove "wrap_field(Field())" duplication.
You can use it as usual Field().
"""


NET_PORT = BaseField(description="Port number.", examples=[8080], gt=0, le=65535)

TIMESTAMP = BaseField(description="Timestamp in seconds since UNIX epoch.", examples=[1610000000], ge=0)
DATETIME = BaseField(description="Date and time in ISO 8601 format.", examples=["2021-01-07T12:00:00Z"])

UUID = BaseField(
    description="UUID version 4.",
    examples=["123e4567-e89b-12d3-a456-426614174000"],
)
ID = BaseField(
    description="Unique integer autoincrementing identifier.",
    examples=[1],
    ge=0,
)
DELETED_INCLUSION_FILTER = BaseField(
    description="Object deleted inclusion filter.",
    default=None,
    filter_type=FilterType.func,
    filter_func=inclusion_filter,
    table_column="deleted_at",
)
