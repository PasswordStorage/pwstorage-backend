"""Folder-related exceptions."""

from .abc import AbstractException, NotFoundException


class FolderException(AbstractException):
    """Base folder exception."""


class FolderNotFoundException(FolderException, NotFoundException):
    """Folder not found."""

    auto_additional_info_fields = ["folder_id"]

    detail = "Folder {folder_id} not found"
