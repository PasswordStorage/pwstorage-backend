"""Version 1 API."""

from fastapi import APIRouter

from . import auth, auth_session, folder, ping, record, user


router = APIRouter(prefix="/v1")

for i in [
    ping.router,
    auth.router,
    user.router,
    auth_session.router,
    folder.router,
    record.router,
]:
    router.include_router(i)
