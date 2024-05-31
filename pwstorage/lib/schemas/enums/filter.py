"""Filter types."""

from .abc import BaseEnum


class FilterType(BaseEnum):
    """Filter types."""

    eq = "eq"
    """Equals."""
    ne = "ne"
    """Not equals."""
    gt = "gt"
    """Greater than."""
    ge = "ge"
    """Greater than or equal."""
    lt = "lt"
    """Less than."""
    le = "le"
    """Less than or equal."""
    like = "like"
    """Like."""
    ilike = "ilike"
    """Case-insensitive like."""
    skip = "skip"
    """Skip auto-generated filter."""
    func = "func"
    """Function filter."""
