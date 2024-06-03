"""Record-related exceptions."""

from .abc import AbstractException, NotFoundException


class RecordException(AbstractException):
    """Base record exception."""


class RecordNotFoundException(RecordException, NotFoundException):
    """Record not found."""

    auto_additional_info_fields = ["record_id"]

    detail = "Record {record_id} not found"
