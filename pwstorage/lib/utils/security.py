"""Security utilities."""

from datetime import datetime, timedelta, timezone
from hashlib import blake2b
from typing import Any

from jwt import encode as jwt_encode


def hash_text(text: str | bytes, *, digest_size: int = 64, salt: str | bytes | None = None) -> str:
    """Hash text."""
    return blake2b(
        (text if isinstance(text, bytes) else text.encode()),
        digest_size=digest_size,
        salt=((salt if isinstance(salt, bytes) else salt.encode()) if salt else b""),
    ).hexdigest()


def hash_password(password: str) -> str:
    """Hash password."""
    return hash_text(password, salt=hash_text(password[::2], digest_size=8))


def create_jwt(data: Any, secret_key: str = "", algorithm: str | None = None, expires_in: int = 15) -> str:
    """Create JWT."""
    return jwt_encode(
        {"sub": str(data), "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in)},
        secret_key,
        algorithm=algorithm,
    )
