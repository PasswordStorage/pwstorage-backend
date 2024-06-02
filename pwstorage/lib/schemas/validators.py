"""Pydantic validators."""

from re import compile as re_compile

from pydantic import AfterValidator, BeforeValidator


def not_empty(s: str) -> str:
    """Not empty."""
    if not s:
        raise ValueError("cannot be empty")
    return s


def strip(s: str) -> str:
    """Strip."""
    if not isinstance(s, str):
        raise ValueError("must be a string")
    return s.strip()


def check_special_characters(s: str) -> str:
    """Check special characters."""
    for i, c in enumerate(["\n", "\r", "\t"]):
        if c in s:
            raise ValueError(f"cannot contain special characters (debug: elem at index {i})")
    return s


def check_text(text: str) -> str:
    """Check text."""
    if not isinstance(text, str):
        raise ValueError("must be a string")
    return check_special_characters(strip(not_empty(text)))


def python_regex(
    regex: str,
    flags: int = 0,
    include_regex_in_error_message: bool = True,
    limit_length: int | None = None,
) -> AfterValidator:
    """Regex validation.

    Regex validation with python backend (instead of pydantic rust pattern backend,
    that does not fully support all regex features and crashes fastapi openapi generation).

    Use this validator carefully as it can be resource consuming, use it as the last validator.

    Args:
        regex (str): Regex string.
        flags (int, optional): Regex flags. Defaults to 0.
        include_regex_in_error_message (bool, optional): Include regex in error message. Defaults to True.
        limit_length (int | None, optional): Limit length of string (less or equal). Defaults to None.

    Returns:
        AfterValidator: Validator.

    Example:
        >>> RecipeName = Annotated[str, python_regex("^[a-zA-Z0-9_ -]+$")]
        >>> class Recipe(BaseModel):
        ...     name: RecipeName = Field(max_length=32)
    """
    compiled = re_compile(regex, flags)

    def python_regex_inner(s: str | None) -> str | None:
        if s is None:
            return s
        if limit_length is not None and len(s) > limit_length:
            raise ValueError(f"length must be less than or equal to {limit_length}")
        if not compiled.match(s):
            raise ValueError(
                ("does not match regex: " + regex) if include_regex_in_error_message else "does not match regex"
            )
        return s

    return AfterValidator(python_regex_inner)


NotEmptyValidator = AfterValidator(not_empty)
StripValidator = BeforeValidator(strip)
CheckSpecialCharactersValidator = AfterValidator(check_special_characters)
CheckTextValidator = BeforeValidator(check_text)
