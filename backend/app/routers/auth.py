from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from models.organization import User

from ..deps import CurrentUser, DbSession, log_audit
from ..security import create_access_token, verify_pin

router = APIRouter(prefix="/auth", tags=["Auth"])


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


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: DbSession) -> dict[str, Any]:
    """Authenticate agent or supervisor via Phone + PIN."""
    # Active users scan (EncryptedString decrypts automatically)
    res = await db.execute(select(User).where(User.active == True))  # noqa: E712
    users = res.scalars().all()

    matched_user = None
    clean_req_phone = req.phone.strip().replace(" ", "").replace("-", "")
    if clean_req_phone.startswith("+91"):
        clean_req_phone = clean_req_phone[3:]

    for u in users:
        u_phone = (u.phone or "").strip().replace(" ", "").replace("-", "")
        if u_phone.startswith("+91"):
            u_phone = u_phone[3:]
        if u_phone == clean_req_phone:
            matched_user = u
            break

    if not matched_user or not verify_pin(req.pin, matched_user.pin_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or PIN",
        )

    token = create_access_token(
        user_id=matched_user.id,
        role=matched_user.role.value,
        org_id=matched_user.org_id,
    )

    await log_audit(
        db=db,
        actor_id=matched_user.id,
        action="LOGIN",
        entity="users",
        entity_id=str(matched_user.id),
    )
    await db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": matched_user.id,
            "name": matched_user.name,
            "role": matched_user.role.value,
            "org_id": matched_user.org_id,
            "lang": matched_user.lang,
        },
    }


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser) -> dict[str, Any]:
    """Get authenticated user identity."""
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role.value,
        "org_id": user.org_id,
        "lang": user.lang,
    }
