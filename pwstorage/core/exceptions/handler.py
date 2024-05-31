"""Default exception handlers for the intape package."""

import logging
from typing import Any
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .abc import AbstractException


logger = logging.getLogger(__name__)

EMPTY_EXCEPTION_UUID = "00000000-0000-0000-0000-000000000000"


class ErrorSchema(BaseModel):
    """Error response for AbstractException."""

    detail: str | None = Field(
        description="Optional exception detail. Public and can be showed to the user.",
        examples=["Server 1 not found."],
    )
    error_code: str = Field(description="Exception name.", examples=["ServerNotFoundException"])
    event_id: str | UUID = Field(
        description="Exception event UUID. Can be used to track exceptions. "
        "Can be provided to support team to request for more details. "
        "If it equals zero, then exception is not tracked.",
    )
    additional_info: dict[str, Any] = Field(
        description="Additional computer-readable information.", examples=[{"server_id": 1}]
    )


async def abstract_exception_handler(request: Request, exc: AbstractException, log: bool = True) -> JSONResponse:
    """Exception handler for AbstractException.

    Returns:
        JSON serialized ErrorModel.
    """
    if log:
        exc._log()

    if exc.is_public:
        return JSONResponse(
            status_code=exc.current_status_code,
            content=ErrorSchema(
                error_code=exc.__class__.__name__,
                detail=exc.current_detail,
                event_id=str(exc.current_request_id),
                additional_info=exc.current_additional_info,
            ).model_dump(mode="json"),
            headers=exc.current_headers,
        )
    else:
        return await unknown_exception_handler(request, exc, exc.current_request_id)


async def unknown_exception_handler(request: Request, exc: Exception, id_: UUID | None = None) -> JSONResponse:
    """Exception handler for unknown exceptions.

    Returns:
        JSON serialized ErrorModel.
    """
    if id_ is None:
        id_ = uuid4()
    logger.exception(f"({id_}) Unknown exception occurred. Details:")

    return JSONResponse(
        status_code=500,
        content=ErrorSchema(
            error_code="UnknownException",
            detail="Unknown exception occurred.",
            event_id=str(id_),
            additional_info={},
        ).model_dump(mode="json"),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Exception handler for HTTPException.

    Returns:
        JSON serialized ErrorModel.
    """
    id_ = uuid4()
    logger.exception(f"({id_}) Raw HTTPException occurred. Details:")

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorSchema(
            error_code="Exception",
            detail=exc.detail,
            event_id=str(id_),
            additional_info={},
        ).model_dump(mode="json"),
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Exception handler for RequestValidationError.

    Returns:
        JSON serialized ErrorModel.
    """
    errors = exc.errors()
    for error in errors:
        if "ctx" in error:
            del error["ctx"]
        if "url" in error:
            del error["url"]
    schema = ErrorSchema(
        error_code="ValidationException",
        detail="Invalid request data.",
        event_id=EMPTY_EXCEPTION_UUID,
        additional_info={"errors": errors},
    ).model_dump(mode="json")
    return JSONResponse(
        status_code=422,
        content=schema,
    )


async def not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Exception handler for 404.

    Returns:
        JSON serialized ErrorModel.
    """
    r = ErrorSchema(
        error_code="EndpointNotFoundException",
        detail="404 endpoint not found.",
        event_id=EMPTY_EXCEPTION_UUID,
        additional_info={},
    ).model_dump(mode="json")
    r["additional_info"]["urls"] = {
        "openapi": "/openapi.json",
        "docs": "/docs",
    }
    return JSONResponse(status_code=404, content=r)


def regiter_exception_handlers(app: FastAPI) -> None:
    """Register default exception handlers.

    Args:
        app: FastAPI application.
    """
    app.add_exception_handler(AbstractException, abstract_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unknown_exception_handler)
    app.add_exception_handler(404, not_found_exception_handler)  # type: ignore[arg-type]
