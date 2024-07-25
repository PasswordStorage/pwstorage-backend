"""Sentry configuration."""

import logging
from os import environ

from sentry_sdk import init as sentry_sdk_init
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration


def configure_sentry(
    dsn: str | None = None, *, asyncio_integration: bool = True, fastapi_integration: bool = True
) -> None:
    """Configure Sentry."""
    dsn = dsn or environ.get("SENTRY_DSN")
    if dsn is None:
        return

    integrations: list[Integration] = []
    integrations.append(LoggingIntegration(level=logging.DEBUG))
    if asyncio_integration:
        integrations.append(AsyncioIntegration())
    if fastapi_integration:
        integrations.append(FastApiIntegration())
        integrations.append(StarletteIntegration())

    sentry_sdk_init(
        dsn=dsn,
        enable_tracing=True,
        integrations=integrations,
        traces_sample_rate=0.5,
    )
