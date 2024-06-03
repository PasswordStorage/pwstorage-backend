"""Security utilities."""

from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from hashlib import blake2b
from typing import Any

from cryptography.fernet import Fernet
from jwt import decode as jwt_decode, encode as jwt_encode


class Encryptor:
    """Encryptor."""

    def __init__(self, secret_key: str, jwt_algorithm: str, expire_minutes: int = 15):
        self.__secret_key = secret_key
        self.__jwt_algorithm = jwt_algorithm
        self.__expire_minutes = expire_minutes

    @property
    def jwt_expire_minutes(self) -> int:
        """JWT expire minutes."""
        return self.__expire_minutes

    def encrypt_text(self, text: str, key: str = "") -> str:
        """Encrypt text."""
        return Fernet(self.__get_encryption_key(key)).encrypt(text.encode()).decode()

    def decrypt_text(self, text: str, key: str = "") -> str:
        """Decrypt text."""
        return Fernet(self.__get_encryption_key(key)).decrypt(text).decode()

    def encode_jwt(self, data: Any, expires_in: int | None = None) -> str:
        """Encode JWT."""
        return jwt_encode(
            {
                "sub": str(data),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in or self.__expire_minutes),
            },
            self.__secret_key,
            algorithm=self.__jwt_algorithm,
        )

    def decode_jwt(self, token: str) -> dict[str, Any]:
        """Decode JWT."""
        return jwt_decode(token, key=self.__secret_key, algorithms=[self.__jwt_algorithm])

    @staticmethod
    def hash_text(text: str | bytes, *, digest_size: int = 64, salt: str | bytes | None = None) -> str:
        """Hash text."""
        return blake2b(
            (text if isinstance(text, bytes) else text.encode()),
            digest_size=digest_size,
            salt=((salt if isinstance(salt, bytes) else salt.encode()) if salt else b""),
        ).hexdigest()

    @staticmethod
    def hash_password(password: str, *, digest_size: int = 64) -> str:
        """Hash password."""
        return Encryptor.hash_text(
            password, digest_size=digest_size, salt=Encryptor.hash_text(password[::2], digest_size=8)
        )

    def __get_encryption_key(self, key: str) -> bytes:
        return urlsafe_b64encode(Encryptor.hash_text(f"{key}{self.__secret_key}", digest_size=16).encode())
