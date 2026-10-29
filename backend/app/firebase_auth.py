"""Verify Firebase Authentication ID tokens (phone sign-in) without the Admin SDK."""

from __future__ import annotations

import time
from typing import Any

import httpx
import jwt
from cryptography.x509 import load_pem_x509_certificate

from .config import settings

CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_cache: dict[str, Any] = {"certs": {}, "exp": 0.0}


class FirebaseTokenError(ValueError):
    pass


async def _certs() -> dict[str, str]:
    if _cache["certs"] and _cache["exp"] > time.time():
        return _cache["certs"]
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(CERTS_URL)
    res.raise_for_status()
    max_age = 3600
    for part in res.headers.get("cache-control", "").split(","):
        if part.strip().startswith("max-age="):
            max_age = int(part.strip()[8:])
    _cache.update(certs=res.json(), exp=time.time() + max_age)
    return _cache["certs"]


async def verify_firebase_phone_token(id_token: str) -> str:
    """Return the verified E.164 phone number from a Firebase ID token, or raise."""
    project = settings.firebase_project_id
    if not project:
        raise FirebaseTokenError("Firebase is not configured")
    try:
        kid = jwt.get_unverified_header(id_token).get("kid")
    except jwt.PyJWTError as e:
        raise FirebaseTokenError("Malformed token") from e
    pem = (await _certs()).get(kid or "")
    if not pem:
        raise FirebaseTokenError("Unknown signing key")
    key = load_pem_x509_certificate(pem.encode()).public_key()
    try:
        claims = jwt.decode(
            id_token, key, algorithms=["RS256"], audience=project,
            issuer=f"https://securetoken.google.com/{project}", leeway=30,
        )
    except jwt.PyJWTError as e:
        raise FirebaseTokenError("Invalid or expired token") from e
    phone = claims.get("phone_number")
    if not phone or claims.get("firebase", {}).get("sign_in_provider") != "phone":
        raise FirebaseTokenError("Token is not from phone sign-in")
    return phone
