"""Pydantic validators."""

from re import compile as re_compile

from pydantic import AfterValidator, BeforeValidator


def not_empty(s: str) -> str:
    """Ensure the string is not empty.

    Args:
        s (str): The input string.

    Returns:
        str: The input string if it is not empty.

    Raises:
        ValueError: If the input string is empty.
    """
    if not s:
        raise ValueError("cannot be empty")
    return s


def strip(s: str) -> str:
    """Strip leading and trailing whitespace from the string.

    Args:
        s (str): The input string.

    Returns:
        str: The stripped string.

    Raises:
        ValueError: If the input is not a string.
    """
    if not isinstance(s, str):
        raise ValueError("must be a string")
    return s.strip()


def check_special_characters(s: str) -> str:
    """Ensure the string does not contain special characters.

    Args:
        s (str): The input string.

    Returns:
        str: The input string if it does not contain special characters.

    Raises:
        ValueError: If the input string contains special characters.
    """
    for i, c in enumerate(["\n", "\r", "\t"]):
        if c in s:
            raise ValueError(f"cannot contain special characters (debug: elem at index {i})")
    return s


def check_text(text: str) -> str:
    """Perform a series of checks on the text.

    Args:
        text (str): The input text.

    Returns:
        str: The validated text.

    Raises:
        ValueError: If the input is not a string or fails any of the checks.
    """
    if not isinstance(text, str):
        raise ValueError("must be a string")
    return check_special_characters(strip(not_empty(text)))


def python_regex(
    regex: str,
    flags: int = 0,
    include_regex_in_error_message: bool = True,
    limit_length: int | None = None,
) -> AfterValidator:
    """Create a regex validator using Python's regex engine.

    This validator uses Python's regex engine instead of Pydantic's Rust-based pattern backend, which may not support
    all regex features and can cause issues with FastAPI's OpenAPI generation.

    Args:
        regex (str): The regex pattern.
        flags (int, optional): Regex flags. Defaults to 0.
        include_regex_in_error_message (bool, optional): Include the regex pattern
            in the error message. Defaults to True.
        limit_length (int | None, optional): Limit the length of the string. Defaults to None.

    Returns:
        AfterValidator: The regex validator.

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


# Validators
NotEmptyValidator = AfterValidator(not_empty)
StripValidator = BeforeValidator(strip)
CheckSpecialCharactersValidator = AfterValidator(check_special_characters)
CheckTextValidator = BeforeValidator(check_text)
