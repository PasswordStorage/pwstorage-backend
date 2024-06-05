"""Version 1 API."""

from fastapi import APIRouter

from . import auth, folder, ping, record, user


router = APIRouter(prefix="/v1")

for i in [
    ping.router,
    auth.router,
    user.router,
    folder.router,
    record.router,
]:
    router.include_router(i)
