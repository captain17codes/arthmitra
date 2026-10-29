"""
Encryption helpers for DPDP Act 2023 compliance and sensitive PII columns.
Uses AES-GCM via Cryptography's Fernet with key derivation.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import String, TypeDecorator

from .config import settings

_PH = PasswordHasher()


def hash_pin(pin: str) -> str:
    """Hash PIN using Argon2id."""
    return _PH.hash(pin)


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verify PIN against Argon2id hash."""
    try:
        return _PH.verify(pin_hash, pin)
    except Exception:
        return False


def normalize_phone(raw: str) -> str | None:
    """Return a 10-digit Indian mobile number, or None if invalid."""
    digits = "".join(ch for ch in (raw or "") if ch.isdigit())
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 10 and digits[0] in "6789":
        return digits
    return None


def keyed_hash(value: str, purpose: str) -> str:
    """HMAC-SHA256 so phone/OTP hashes cannot be brute-forced without the server key."""
    key = (settings.encryption_key or settings.secret_key).encode("utf-8")
    return hmac.new(key, f"{purpose}:{value}".encode(), hashlib.sha256).hexdigest()


def phone_hash(phone: str) -> str:
    return keyed_hash(phone, "phone")


def create_setup_token(phone: str, minutes: int = 15) -> str:
    """Short-lived token proving OTP verification; only usable to set a PIN."""
    now = datetime.now(UTC)
    payload = {"typ": "pin_setup", "ph": phone_hash(phone), "phone": phone, "iat": now,
               "exp": now + timedelta(minutes=minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_setup_token(token: str) -> dict[str, Any] | None:
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    return data if data.get("typ") == "pin_setup" else None


def create_access_token(
    user_id: int, role: str, org_id: int, expires_delta: timedelta | None = None
) -> str:
    """Generate signed JWT token."""
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "role": role,
        "org_id": org_id,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate signed JWT token."""
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    return None if data.get("typ") == "pin_setup" else data


def _derive_fernet_key(secret: str) -> bytes:
    """Derive a URL-safe base64 32-byte key from secret_key."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_FERNET_INSTANCE = Fernet(_derive_fernet_key(settings.encryption_key or settings.secret_key))


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
