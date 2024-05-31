"""Tools for generating OpenAPI schema."""

from importlib import import_module
from typing import Any, Sequence

from fastapi.openapi.utils import get_openapi as fastapi_get_openapi
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from pwstorage.core.exceptions.abc import AbstractException


def get_openapi(
    *,
    title: str,
    version: str,
    openapi_version: str = "3.1.0",
    summary: str | None = None,
    description: str | None = None,
    routes: Sequence[BaseRoute],
    webhooks: Sequence[BaseRoute] | None = None,
    tags: list[dict[str, Any]] | None = None,
    servers: list[dict[str, str | Any]] | None = None,
    terms_of_service: str | None = None,
    contact: dict[str, str | Any] | None = None,
    license_info: dict[str, str | Any] | None = None,
    logo_url: str | None = "https://w3s.link/ipfs/bafybeibdusnw63pr4a6otvtl6eqrydw7vi7l2r6q5p4woyltthmiipj77u/logo.png",
    exclude_tags: Sequence[str] | None = None,
    remove_tags: Sequence[str] | None = ["internal"],
) -> dict[str, Any]:
    """Generate OpenAPI schema."""
    openapi_schema = fastapi_get_openapi(
        title=title,
        version=version,
        openapi_version=openapi_version,
        summary=summary,
        description=description,
        routes=routes,
        webhooks=webhooks,
        tags=tags,
        servers=servers,
        terms_of_service=terms_of_service,
        contact=contact,
        license_info=license_info,
    )
    # default uuid
    default_uuid = "4c82a181-df68-46ea-b94b-b565c6517d93"
    # Add logo
    if logo_url is not None:
        openapi_schema["info"]["x-logo"] = {"url": logo_url}

    all_exceptions: set[type[AbstractException]] = set()
    methods_to_remove: set[tuple[str, str]] = set()
    # Iterate over all paths
    for path_url, path in openapi_schema["paths"].items():
        # Iterate over all methods
        for method_name, method in path.items():
            # If the method has tags that are excluded, remove the method
            if exclude_tags is not None and any(tag in exclude_tags for tag in method.get("tags", [])):
                methods_to_remove.add((path_url, method_name))
                continue
            # If the method has tags that are removed, remove the tags
            method["tags"] = list(filter(lambda tag: tag not in (remove_tags or []), method.get("tags", [])))
            # If method has "exceptions" field, then add exception responses
            if method.get("exceptions"):
                exceptions = method.pop("exceptions")
                for exception_path in sorted(exceptions):
                    # exception is a path to the exception class, import it
                    exception: type[Exception] = getattr(
                        import_module(".".join(exception_path.split(".")[:-1])), exception_path.split(".")[-1]
                    )
                    if not issubclass(exception, AbstractException):
                        raise TypeError(f"{exception} is not a subclass of AbstractException")
                    # Add exception to all_exceptions
                    all_exceptions.add(exception)
                    # Add exception to responses
                    if str(exception.status_code) not in method["responses"]:
                        method["responses"][str(exception.status_code)] = {
                            "description": exception.__name__,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{exception.__name__}",
                                    }
                                }
                            },
                        }
                    else:
                        method["responses"][str(exception.status_code)]["description"] = (
                            "Exceptions: "
                            + method["responses"][str(exception.status_code)]["description"]
                            + ", "
                            + exception.__name__
                        )
                        if (
                            "oneOf"
                            in method["responses"][str(exception.status_code)]["content"]["application/json"]["schema"]
                        ):
                            method["responses"][str(exception.status_code)]["content"]["application/json"]["schema"][
                                "oneOf"
                            ].append({"$ref": f"#/components/schemas/{exception.__name__}"})
                        else:
                            old = method["responses"][str(exception.status_code)]["content"]["application/json"][
                                "schema"
                            ]
                            method["responses"][str(exception.status_code)]["content"]["application/json"]["schema"] = {
                                "oneOf": [
                                    old,
                                    {"$ref": f"#/components/schemas/{exception.__name__}"},
                                ]
                            }
                    # Check if method description contains exception description
                    if method["description"].find("Raises") == -1:
                        method["description"] += "\n\n## Raises:"
                    method[
                        "description"
                    ] += f"\n- **{exception.__name__}** ({exception.status_code}): {exception.detail}"
            # Iterate over parameters and remove additional fields
            for parameter in method.get("parameters", []):
                if parameter["in"] == "query":
                    for field in ["group", "filter_type", "table_column"]:
                        if field in parameter["schema"]:
                            parameter["schema"].pop(field)
    # Remove methods that were excluded
    for path_url, method_name in methods_to_remove:
        del openapi_schema["paths"][path_url][method_name]
    # Iterate over all paths to remove empty paths
    for path in list(openapi_schema["paths"].keys()):
        if len(openapi_schema["paths"][path]) == 0:
            openapi_schema["paths"].pop(path)
    # Iterate over all exceptions and add them to the components
    for exception in sorted(all_exceptions, key=lambda e: e.__name__):
        additional_info: dict[str, Any] = {
            "type": "object",
            "description": "Additional computer-readable information for this exception.",
        }
        if exception.auto_additional_info_fields:
            additional_info["properties"] = {}
            for field in exception.auto_additional_info_fields:
                additional_info["properties"][field] = {
                    "type": "string",
                    "description": "Can be any type (not only string). Field may be omitted.",
                }
        obj = {
            "title": exception.__name__,
            "type": "object",
            "properties": {
                "detail": {"type": "string"} | {"example": exception.detail} if exception.detail is not None else {},
                "error_code": {"type": "string", "example": exception.__name__},
                "event_id": {
                    "type": "string",
                    "format": "uuid",
                    "example": default_uuid,
                    "description": "UUID v4, unique for each event",
                },
                "additional_info": additional_info,
            },
        }
        if exception.detail is not None:
            obj["description"] = exception.detail
        openapi_schema.setdefault("components", {}).setdefault("schemas", {})[exception.__name__] = obj
    # Iterate over all schemas references and add them to set
    schemas_used = set()

    def recurse_schemas(schema: dict[str, Any]) -> None:
        for key, value in schema.items():
            if isinstance(value, dict):
                recurse_schemas(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        recurse_schemas(item)
            elif key == "$ref":
                schemas_used.add(value.split("/")[-1])

    recurse_schemas(openapi_schema)
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
        return openapi_schema
    # Iterate over all schemas and add them to set
    all_schemas = set()
    for schema in openapi_schema["components"]["schemas"].keys():
        all_schemas.add(schema)
    # Find difference between schemas used and all schemas and remove unused schemas
    for schema in all_schemas - schemas_used:
        openapi_schema["components"]["schemas"].pop(schema)
    # Overwrite HTTPValidationError schema
    openapi_schema["components"]["schemas"]["HTTPValidationError"] = openapi_schema["components"]["schemas"].get(
        "HTTPValidationError", {"properties": {}}
    )
    openapi_schema["components"]["schemas"]["HTTPValidationError"]["properties"]["detail"] = {
        "type": "string",
        "example": "Validation error",
        "description": "A human readable error message",
    }
    openapi_schema["components"]["schemas"]["HTTPValidationError"]["properties"]["event_id"] = {
        "type": "string",
        "format": "uuid",
        "example": default_uuid,
        "description": "UUID v4, unique for each event",
    }
    openapi_schema["components"]["schemas"]["HTTPValidationError"]["properties"]["error_code"] = {
        "type": "string",
        "example": "ValidationException",
        "description": "The error code",
    }
    openapi_schema["components"]["schemas"]["HTTPValidationError"]["properties"]["additional_info"] = {
        "type": "object",
        "description": "Additional computer-readable information for this exception.",
        "properties": {
            "errors": {
                "type": "array",
                "description": "A list of validation errors",
                "items": {
                    "type": "object",
                    "properties": {
                        "loc": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "body",
                            },
                        },
                        "msg": {
                            "type": "string",
                            "example": "query -> limit\n  ensure this value is less than or equal to 100 "
                            "(type=value_error.number.not_le; limit_value=100)",
                        },
                        "type": {
                            "type": "string",
                            "example": "value_error.missing",
                        },
                        "ctx": {
                            "type": "object",
                        },
                    },
                },
            },
        },
    }
    del openapi_schema["components"]["schemas"]["ValidationError"]

    return openapi_schema


def exc_list(*exceptions: type[AbstractException]) -> dict[str, Any]:
    """Convert a list of exceptions to a list of their paths."""
    return {"exceptions": [exception.__module__ + "." + exception.__name__ for exception in exceptions]}


def generate_operation_id(route: APIRoute) -> str:
    """Generate a unique id for a route."""
    return route.name
