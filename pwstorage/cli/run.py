"""Server launch related commands."""

import os


try:
    import alembic.config

    _alembic_installed = True
except ModuleNotFoundError:
    _alembic_installed = False

import click
import uvicorn

from .cli import cli


@cli.command()
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind to.")
@click.option("--port", "-p", default=8000, help="Port to bind to.")
@click.option("--migrate", "-m", is_flag=True, help="Run migrations before starting.")
@click.option("--reload", "-r", is_flag=True, help="Reload on code changes.")
@click.option("--workers", "-w", default=1, help="Number of workers.")
@click.option("--env", "-e", multiple=True, help="Environment variables.")
def run(host: str, port: int, migrate: bool, reload: bool, workers: int, env: list[str]) -> None:
    """Run the API webserver."""
    if migrate and not _alembic_installed:
        raise ModuleNotFoundError("alembic is not installed, but --migrate was passed.")
    if migrate and _alembic_installed:
        alembic.config.main(argv=["upgrade", "head"])
    for key, value in [item.split("=") for item in env]:
        os.environ[key.upper()] = value
    uvicorn.run(
        "pwstorage.app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        factory=True,
    )


@cli.command()
@click.option("--docker", is_flag=True, help="If this is a docker container. (Sets DATABASE__URL for docker-compose)")
def dev(docker: bool) -> None:
    """Run the development server with pre-defined settings."""
    os.environ["PRODUCTION"] = os.environ.get("PRODUCTION", "false")

    database_host = "db" if docker else "localhost"
    os.environ["DATABASE__URL"] = os.environ.get(
        "DATABASE__URL", f"postgresql+asyncpg://user:password@{database_host}/db"
    )

    uvicorn.run(
        "pwstorage.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        workers=1,
        factory=True,
    )
