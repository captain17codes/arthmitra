"""SMS delivery for OTPs. Provider chosen by settings.otp_provider."""

from __future__ import annotations

import logging

import httpx

from .config import settings

log = logging.getLogger("arthmitra.sms")


class SmsError(RuntimeError):
    pass


def is_dev_mode() -> bool:
    return settings.otp_provider.lower() == "dev"


async def send_otp(phone: str, otp: str) -> None:
    """Send the OTP. In dev mode nothing is sent; the caller returns it to the client."""
    provider = settings.otp_provider.lower()
    if provider == "dev":
        log.warning("OTP_PROVIDER=dev: OTP for ******%s not sent by SMS (demo mode)", phone[-4:])
        return
    if provider == "msg91":
        if not (settings.msg91_auth_key and settings.msg91_template_id):
            raise SmsError("MSG91 is not configured")
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(
                "https://control.msg91.com/api/v5/otp",
                params={"template_id": settings.msg91_template_id, "mobile": f"91{phone}", "otp": otp},
                headers={"authkey": settings.msg91_auth_key, "Content-Type": "application/json"},
            )
        if res.status_code >= 400 or (res.json() or {}).get("type") == "error":
            raise SmsError(f"MSG91 rejected the request ({res.status_code})")
        return
    raise SmsError(f"Unknown OTP provider '{settings.otp_provider}'")
