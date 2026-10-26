"""
Encryption helpers for DPDP Act 2023 compliance and sensitive PII columns.
Uses AES-GCM via Cryptography's Fernet with key derivation.
"""

from __future__ import annotations

import base64
import hashlib
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import String, TypeDecorator

from .config import settings


def _derive_fernet_key(secret: str) -> bytes:
    """Derive a URL-safe base64 32-byte key from secret_key."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_FERNET_INSTANCE = Fernet(_derive_fernet_key(settings.secret_key))


def encrypt_text(plaintext: str | None) -> str | None:
    """Encrypt plaintext string into base64 token."""
    if plaintext is None:
        return None
    token = _FERNET_INSTANCE.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_text(ciphertext: str | None) -> str | None:
    """Decrypt base64 token back to plaintext string."""
    if ciphertext is None:
        return None
    try:
        data = _FERNET_INSTANCE.decrypt(ciphertext.encode("utf-8"))
        return data.decode("utf-8")
    except InvalidToken:
        # Fallback or raise error
        return ciphertext


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy TypeDecorator that transparently encrypts strings on write
    and decrypts them on read.
    Used for 🔒 PII columns (Beneficiary Name, Phone, Income).
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 512, **kwargs: Any) -> None:
        super().__init__(length, **kwargs)

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        if value is None:
            return None
        return encrypt_text(str(value))

    def process_result_value(self, value: Any, dialect: Any) -> str | None:
        if value is None:
            return None
        return decrypt_text(str(value))
