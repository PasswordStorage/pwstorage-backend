"""Module containing main FastAPI application."""

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Self

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import AppConfig
from .core.dependencies.app import constructors as app_depends, fastapi as depend_stubs
from .core.exceptions.handler import regiter_exception_handlers
from .lib.utils.openapi import generate_operation_id, get_openapi
from .routers import router
from .version import __version__


class App:
    """FastAPI application."""

    def __init__(self, config: AppConfig, app: FastAPI | None = None) -> None:
        """Initialize FastAPI application.

        Args:
            config (AppConfig): Application config.
            app (FastAPI, optional): FastAPI application. If set to None, a new
                application will be created. If set to an existing FastAPI
                application, it will be used (but not instance configuration
                will be applied).
        """
        self.config = config
        self.app = app or FastAPI(
            title="PasswordStorage",
            description="Password storage API.",
            version=__version__,
            generate_unique_id_function=generate_operation_id,
            lifespan=self.lifespan,
        )

        self.setup_app()

    @classmethod
    def from_env(cls) -> Self:
        """Create application from environment variables."""
        return cls(AppConfig.from_env())

    def setup_app(self) -> None:
        """Add middlewares and routers to FastAPI application."""
        self.app.include_router(router)
        # middlewares
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.general.origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # exception handler
        regiter_exception_handlers(self.app)
        # override openapi schema
        self.app.openapi_schema = get_openapi(
            title=self.app.title,
            description=self.app.description,
            version=self.app.version,
            routes=self.app.routes,
            exclude_tags=["internal", "debug"] if self.config.general.production else [],
        )

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        """Lifespan."""
        async with asynccontextmanager(app_depends.redis_pool)(self.config.redis.url) as redis_pool:
            with contextmanager(app_depends.db_session_maker)(self.config.database.url) as maker:
                app.dependency_overrides[depend_stubs.app_config_stub] = lambda: self.config
                app.dependency_overrides[depend_stubs.db_session_maker_stub] = lambda: maker
                app.dependency_overrides[depend_stubs.redis_conn_pool_stub] = lambda: redis_pool

                yield


def app() -> FastAPI:
    """Return FastAPI application.

    This function is used by Uvicorn to run the application.
    """
    return App.from_env().app
