from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select

from models.auth_otp import OtpCode
from models.beneficiary import Beneficiary, Consent
from models.case import Advisory, Case, CaseInput, DprDocument, Evaluation
from models.enums import OrgType, UserRole
from models.organization import Organization, User

from ..deps import CurrentUser, DbSession, log_audit
from ..security import (
    create_access_token,
    create_setup_token,
    decode_setup_token,
    hash_pin,
    keyed_hash,
    normalize_phone,
    phone_hash,
    verify_pin,
)
from ..sms import SmsError, is_dev_mode, send_otp

router = APIRouter(prefix="/auth", tags=["Auth"])

OTP_TTL = timedelta(minutes=5)
OTP_MAX_ATTEMPTS = 5
OTP_MAX_PER_WINDOW = 3
OTP_WINDOW = timedelta(minutes=15)
OTP_RESEND_GAP = timedelta(seconds=30)
PIN_MAX_FAILURES = 5
PIN_LOCK = timedelta(minutes=15)


class LoginRequest(BaseModel):
    phone: str = Field(..., description="10-digit mobile number")
    pin: str = Field(..., description="4-6 digit numerical PIN")


class UserOut(BaseModel):
    id: int
    name: str
    role: str
    org_id: int
    lang: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class OtpRequest(BaseModel):
    phone: str


class OtpVerify(BaseModel):
    phone: str
    otp: str = Field(..., min_length=4, max_length=8)


class PinSetup(BaseModel):
    setup_token: str
    pin: str = Field(..., pattern=r"^\d{4}$")
    name: str | None = Field(default=None, max_length=100)
    lang: str = "mr"


def _now() -> datetime:
    return datetime.now(UTC)


def _aware(dt: datetime | None) -> datetime | None:
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def _user_out(u: User) -> dict[str, Any]:
    return {"id": u.id, "name": u.name, "role": u.role.value, "org_id": u.org_id, "lang": u.lang}


def _login_payload(u: User) -> dict[str, Any]:
    token = create_access_token(user_id=u.id, role=u.role.value, org_id=u.org_id)
    return {"access_token": token, "token_type": "bearer", "user": _user_out(u)}


async def _find_user(db: DbSession, phone: str) -> User | None:
    """Active user by phone: hash lookup first, then a scan for rows created before phone_hash existed."""
    ph = phone_hash(phone)
    res = await db.execute(select(User).where(User.phone_hash == ph, User.active == True))  # noqa: E712
    u = res.scalars().first()
    if u:
        return u
    res = await db.execute(select(User).where(User.phone_hash.is_(None), User.active == True))  # noqa: E712
    for cand in res.scalars().all():
        if normalize_phone(cand.phone or "") == phone:
            cand.phone_hash = ph  # backfill
            return cand
    return None


def _bad_phone() -> HTTPException:
    return HTTPException(status_code=422, detail="Enter a valid 10-digit mobile number")


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: DbSession) -> dict[str, Any]:
    """Daily login with mobile number + PIN. Locks for 15 minutes after 5 wrong PINs."""
    phone = normalize_phone(req.phone)
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone number or PIN")
    if not phone:
        raise invalid
    user = await _find_user(db, phone)
    if not user:
        raise invalid

    locked_until = _aware(user.locked_until)
    if locked_until and locked_until > _now():
        mins = max(1, int((locked_until - _now()).total_seconds() // 60) + 1)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many wrong PINs. Try again in {mins} minutes or reset your PIN with OTP.",
        )

    if not verify_pin(req.pin, user.pin_hash):
        user.failed_pin_attempts = (user.failed_pin_attempts or 0) + 1
        if user.failed_pin_attempts >= PIN_MAX_FAILURES:
            user.locked_until = _now() + PIN_LOCK
            user.failed_pin_attempts = 0
        await db.commit()
        raise invalid

    user.failed_pin_attempts = 0
    user.locked_until = None
    await log_audit(db=db, actor_id=user.id, action="LOGIN", entity="users", entity_id=str(user.id))
    await db.commit()
    return _login_payload(user)


@router.post("/otp/request")
async def request_otp(req: OtpRequest, db: DbSession) -> dict[str, Any]:
    """Send a 6-digit OTP for sign-up or PIN reset. Rate limited per number."""
    phone = normalize_phone(req.phone)
    if not phone:
        raise _bad_phone()
    ph = phone_hash(phone)
    now = _now()

    recent = (
        await db.execute(
            select(OtpCode).where(OtpCode.phone_hash == ph, OtpCode.created_at >= now - OTP_WINDOW)
            .order_by(OtpCode.created_at.desc())
        )
    ).scalars().all()
    if len(recent) >= OTP_MAX_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Too many OTP requests. Please wait 15 minutes.")
    if recent and _aware(recent[0].created_at) > now - OTP_RESEND_GAP:
        raise HTTPException(status_code=429, detail="Please wait 30 seconds before asking for a new OTP.")

    otp = f"{secrets.randbelow(1_000_000):06d}"
    db.add(OtpCode(phone_hash=ph, code_hash=keyed_hash(otp, "otp:" + ph), expires_at=now + OTP_TTL))
    try:
        await send_otp(phone, otp)
    except SmsError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Could not send SMS: {e}") from e
    await db.commit()

    out: dict[str, Any] = {"sent": True, "expires_in_seconds": int(OTP_TTL.total_seconds())}
    if is_dev_mode():
        out["dev_otp"] = otp  # demo mode only: no SMS provider configured yet
    return out


@router.post("/otp/verify")
async def verify_otp(req: OtpVerify, db: DbSession) -> dict[str, Any]:
    """Check the OTP. Returns a short-lived token used to set (or reset) the PIN."""
    phone = normalize_phone(req.phone)
    if not phone:
        raise _bad_phone()
    ph = phone_hash(phone)
    now = _now()
    code = (
        await db.execute(
            select(OtpCode)
            .where(OtpCode.phone_hash == ph, OtpCode.consumed_at.is_(None))
            .order_by(OtpCode.created_at.desc())
            .limit(1)
        )
    ).scalars().first()
    wrong = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong or expired OTP")
    if not code or _aware(code.expires_at) < now or code.attempts >= OTP_MAX_ATTEMPTS:
        raise wrong
    if not secrets.compare_digest(code.code_hash, keyed_hash(req.otp.strip(), "otp:" + ph)):
        code.attempts += 1
        await db.commit()
        raise wrong

    code.consumed_at = now
    user = await _find_user(db, phone)
    await db.commit()
    return {
        "setup_token": create_setup_token(phone),
        "is_new_user": user is None,
        "name": user.name if user else None,
    }


@router.post("/pin", response_model=LoginResponse)
async def set_pin(req: PinSetup, db: DbSession) -> dict[str, Any]:
    """After OTP: create the account (new number) or reset the PIN (existing), then log in."""
    data = decode_setup_token(req.setup_token)
    phone = normalize_phone((data or {}).get("phone", ""))
    if not data or not phone or data.get("ph") != phone_hash(phone):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP session expired. Please verify again.")

    user = await _find_user(db, phone)
    if user is None:
        name = (req.name or "").strip()
        if not name:
            raise HTTPException(status_code=422, detail="Please enter your name")
        org = Organization(name="Individual", type=OrgType.INDIVIDUAL)
        db.add(org)
        await db.flush()
        user = User(
            org_id=org.id,
            role=UserRole.CITIZEN,
            name=name,
            phone=phone,
            phone_hash=phone_hash(phone),
            pin_hash=hash_pin(req.pin),
            lang=req.lang if req.lang in ("mr", "hi", "en") else "mr",
        )
        db.add(user)
        await db.flush()
        await log_audit(db=db, actor_id=user.id, action="SIGN_UP", entity="users", entity_id=str(user.id))
    else:
        user.pin_hash = hash_pin(req.pin)
        user.failed_pin_attempts = 0
        user.locked_until = None
        if req.name and req.name.strip():
            user.name = req.name.strip()
        await log_audit(db=db, actor_id=user.id, action="PIN_RESET", entity="users", entity_id=str(user.id))
    await db.commit()
    await db.refresh(user)
    return _login_payload(user)


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser) -> dict[str, Any]:
    """Get authenticated user identity."""
    return _user_out(user)


@router.delete("/me")
async def delete_my_account(user: CurrentUser, db: DbSession) -> dict[str, Any]:
    """
    DPDP right to erasure for a self-registered person: deletes their account, profile,
    business plans, evaluations and generated DPR files. Only an anonymous audit line remains.
    """
    if user.role != UserRole.CITIZEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only personal accounts can be self-deleted")

    files = (
        await db.execute(
            select(DprDocument.object_key)
            .join(Evaluation, DprDocument.evaluation_id == Evaluation.id)
            .join(Case, Evaluation.case_id == Case.id)
            .join(Beneficiary, Case.beneficiary_id == Beneficiary.id)
            .where(Beneficiary.org_id == user.org_id)
        )
    ).scalars().all()
    n_cases = (
        await db.execute(
            select(func.count(Case.id)).join(Beneficiary).where(Beneficiary.org_id == user.org_id)
        )
    ).scalar_one()

    ph = user.phone_hash
    org_id, user_id = user.org_id, user.id
    # Explicit child-first deletes (works even where the DB does not enforce ON DELETE CASCADE).
    ben_ids = select(Beneficiary.id).where(Beneficiary.org_id == org_id).scalar_subquery()
    case_ids = select(Case.id).where(Case.beneficiary_id.in_(ben_ids)).scalar_subquery()
    ev_ids = select(Evaluation.id).where(Evaluation.case_id.in_(case_ids)).scalar_subquery()
    await db.execute(delete(DprDocument).where(DprDocument.evaluation_id.in_(ev_ids)))
    await db.execute(delete(Advisory).where(Advisory.evaluation_id.in_(ev_ids)))
    await db.execute(delete(Evaluation).where(Evaluation.case_id.in_(case_ids)))
    await db.execute(delete(CaseInput).where(CaseInput.case_id.in_(case_ids)))
    await db.execute(delete(Case).where(Case.beneficiary_id.in_(ben_ids)))
    await db.execute(delete(Consent).where(Consent.beneficiary_id.in_(ben_ids)))
    await db.execute(delete(Beneficiary).where(Beneficiary.org_id == org_id))
    await db.execute(delete(User).where(User.id == user_id))
    await db.execute(delete(Organization).where(Organization.id == org_id))
    if ph:
        await db.execute(delete(OtpCode).where(OtpCode.phone_hash == ph))
    await log_audit(db=db, actor_id=None, action="ACCOUNT_ERASED", entity="users", entity_id=str(user_id),
                    diff={"cases_deleted": int(n_cases)})
    await db.commit()

    for key in files:
        try:
            Path(key).unlink(missing_ok=True)
        except OSError:
            pass
    return {"deleted": True}
