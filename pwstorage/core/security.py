"""Security utilities."""

from base64 import urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from hashlib import blake2b
from typing import Any

from cryptography.fernet import Fernet
from jwt import decode as jwt_decode, encode as jwt_encode


class Encryptor:
    """Encryptor class for handling encryption, decryption, JWT encoding/decoding, and hashing."""

    def __init__(self, secret_key: str, jwt_algorithm: str, expire_minutes: int = 15):
        """Initialize Encryptor.

        Args:
            secret_key (str): The secret key used for encryption and JWT encoding.
            jwt_algorithm (str): The algorithm used for JWT encoding.
            expire_minutes (int, optional): The expiration time for JWT tokens in minutes. Defaults to 15 minutes.
        """
        self.__secret_key = secret_key
        self.__jwt_algorithm = jwt_algorithm
        self.__expire_minutes = expire_minutes

    @property
    def jwt_expire_minutes(self) -> int:
        """Get the JWT expiration time in minutes.

        Returns:
            int: The expiration time for JWT tokens in minutes.
        """
        return self.__expire_minutes

    def encrypt_text(self, text: str, key: str = "") -> str:
        """Encrypt text using Fernet encryption.

        Args:
            text (str): The text to encrypt.
            key (str, optional): An additional key to use for encryption. Defaults to an empty string.

        Returns:
            str: The encrypted text.
        """
        return Fernet(self.__get_encryption_key(key)).encrypt(text.encode()).decode()

    def decrypt_text(self, text: str, key: str = "") -> str:
        """Decrypt text using Fernet encryption.

        Args:
            text (str): The encrypted text to decrypt.
            key (str, optional): An additional key to use for decryption. Defaults to an empty string.

        Returns:
            str: The decrypted text.
        """
        return Fernet(self.__get_encryption_key(key)).decrypt(text).decode()

    def encode_jwt(self, data: Any, expires_in: int | None = None) -> str:
        """Encode data into a JWT token.

        Args:
            data (Any): The data to encode into the JWT token.
            expires_in (int, optional): The expiration time for the JWT token in minutes. Defaults to the class setting.

        Returns:
            str: The encoded JWT token.
        """
        return jwt_encode(
            {
                "sub": str(data),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_in or self.__expire_minutes),
            },
            self.__secret_key,
            algorithm=self.__jwt_algorithm,
        )

    def decode_jwt(self, token: str) -> dict[str, Any]:
        """Decode a JWT token.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict[str, Any]: The decoded data from the JWT token.
        """
        return jwt_decode(token, key=self.__secret_key, algorithms=[self.__jwt_algorithm])

    @staticmethod
    def hash_text(text: str | bytes, *, digest_size: int = 64, salt: str | bytes | None = None) -> str:
        """Hash text using the BLAKE2b algorithm.

        Args:
            text (Union[str, bytes]): The text to hash.
            digest_size (int, optional): The size of the hash digest. Defaults to 64.
            salt (Union[str, bytes, optional]): An optional salt to use for hashing. Defaults to None.

        Returns:
            str: The hashed text.
        """
        return blake2b(
            (text if isinstance(text, bytes) else text.encode()),
            digest_size=digest_size,
            salt=((salt if isinstance(salt, bytes) else salt.encode()) if salt else b""),
        ).hexdigest()

    @staticmethod
    def hash_password(password: str, *, digest_size: int = 64) -> str:
        """Hash a password using the BLAKE2b algorithm with a salt.

        Args:
            password (str): The password to hash.
            digest_size (int, optional): The size of the hash digest. Defaults to 64.

        Returns:
            str: The hashed password.
        """
        return Encryptor.hash_text(
            password, digest_size=digest_size, salt=Encryptor.hash_text(password[::2], digest_size=8)
        )

    def __get_encryption_key(self, key: str) -> bytes:
        """Generate an encryption key for Fernet.

        Args:
            key (str): An additional key to use for generating the encryption key.

        Returns:
            bytes: The generated encryption key.
        """
        return urlsafe_b64encode(Encryptor.hash_text(f"{key}{self.__secret_key}", digest_size=16).encode())
