"""Version 1 API."""

from fastapi import APIRouter

from . import auth, folder, record, user


router = APIRouter(prefix="/v1")

for i in [auth.router, user.router, folder.router, record.router]:
    router.include_router(i)
