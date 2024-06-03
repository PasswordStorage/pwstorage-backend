"""Version 1 API."""

from fastapi import APIRouter

from . import auth, folder, user


router = APIRouter(prefix="/v1")

for i in [auth.router, user.router, folder.router]:
    router.include_router(i)
