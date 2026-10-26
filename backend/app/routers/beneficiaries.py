from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from models.beneficiary import Beneficiary, Consent
from models.enums import ConsentMethod, TriState
from models.governance import DeletionRequest

from ..config import settings
from ..deps import CurrentUser, DbSession, log_audit, log_processing

router = APIRouter(prefix="/beneficiaries", tags=["Beneficiaries"])


class ConsentCreate(BaseModel):
    notice_version: str = Field(default_factory=lambda: settings.notice_version_current)
    language: str = "mr"
    method: ConsentMethod = ConsentMethod.VOICE
    audio_sha256: str | None = None
    audio_object_key: str | None = None


class BeneficiaryCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    gender: str = Field(..., description="male, female, other")
    age: int = Field(..., ge=18, le=90)
    category: str = Field(..., description="SC, ST, OBC, VJNT, SBC, General")
    category_verified: bool = False
    disability_40: bool = False
    occupation_flags: list[str] | None = Field(default_factory=list)
    income_band: str = "below_1_lakh"
    education_band: str = "class_10_pass"
    shg_member: bool = False
    prior_subsidy: TriState = TriState.UNKNOWN
    credit_default: TriState = TriState.UNKNOWN
    existing_emi_monthly: Decimal = Decimal("0.00")

    # 🔒 Mandatory Consent Block (DPDP Act Compliance)
    consent: ConsentCreate


class BeneficiaryOut(BaseModel):
    id: int
    org_id: int
    first_name: str
    gender: str
    age: int
    category: str
    category_verified: bool
    disability_40: bool
    occupation_flags: list[str] | None
    income_band: str
    education_band: str
    shg_member: bool
    prior_subsidy: str
    credit_default: str
    existing_emi_monthly: Decimal
    active_consent: bool


@router.post("", response_model=BeneficiaryOut, status_code=status.HTTP_201_CREATED)
async def create_beneficiary(
    req: BeneficiaryCreate,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """
    Create a new beneficiary profile.
    ENFORCEMENT: Profile cannot be saved without explicit, recorded consent.
    """
    if not req.consent or not req.consent.notice_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit beneficiary consent is mandatory before recording any profile data",
        )

    # 1. Create beneficiary
    b = Beneficiary(
        org_id=user.org_id,
        first_name=req.first_name,
        gender=req.gender,
        age=req.age,
        category=req.category,
        category_verified=req.category_verified,
        disability_40=req.disability_40,
        occupation_flags=req.occupation_flags,
        income_band=req.income_band,
        education_band=req.education_band,
        shg_member=req.shg_member,
        prior_subsidy=req.prior_subsidy,
        credit_default=req.credit_default,
        existing_emi_monthly=req.existing_emi_monthly,
        created_by=user.id,
    )
    db.add(b)
    await db.flush()

    # 2. Record consent
    c = Consent(
        beneficiary_id=b.id,
        notice_version=req.consent.notice_version,
        language=req.consent.language,
        method=req.consent.method,
        audio_sha256=req.consent.audio_sha256,
        audio_object_key=req.consent.audio_object_key,
        agent_id=user.id,
    )
    db.add(c)

    # 3. Audit & Processing Logs
    await log_audit(
        db=db,
        actor_id=user.id,
        action="CREATE",
        entity="beneficiaries",
        entity_id=str(b.id),
        diff={"category": req.category, "consent_method": req.consent.method.value},
    )
    await log_processing(
        db=db,
        actor_id=user.id,
        purpose="Beneficiary profile creation with verified consent",
        entity="beneficiaries",
        entity_id=str(b.id),
    )

    await db.commit()
    await db.refresh(b)

    return {
        "id": b.id,
        "org_id": b.org_id,
        "first_name": b.first_name,
        "gender": b.gender,
        "age": b.age,
        "category": b.category,
        "category_verified": b.category_verified,
        "disability_40": b.disability_40,
        "occupation_flags": b.occupation_flags,
        "income_band": b.income_band,
        "education_band": b.education_band,
        "shg_member": b.shg_member,
        "prior_subsidy": b.prior_subsidy.value,
        "credit_default": b.credit_default.value,
        "existing_emi_monthly": b.existing_emi_monthly,
        "active_consent": True,
    }


@router.get("", response_model=list[BeneficiaryOut])
async def list_beneficiaries(
    user: CurrentUser,
    db: DbSession,
) -> list[dict[str, Any]]:
    """List beneficiaries within user's organization."""
    res = await db.execute(
        select(Beneficiary)
        .where(Beneficiary.org_id == user.org_id, Beneficiary.deleted_at.is_(None))
        .order_by(Beneficiary.created_at.desc())
    )
    beneficiaries = res.scalars().all()

    # Log DPDP data processing access
    await log_processing(
        db=db,
        actor_id=user.id,
        purpose="List beneficiaries for case intake",
        entity="beneficiaries",
        entity_id=f"org_{user.org_id}",
    )
    await db.commit()

    return [
        {
            "id": b.id,
            "org_id": b.org_id,
            "first_name": b.first_name,
            "gender": b.gender,
            "age": b.age,
            "category": b.category,
            "category_verified": b.category_verified,
            "disability_40": b.disability_40,
            "occupation_flags": b.occupation_flags,
            "income_band": b.income_band,
            "education_band": b.education_band,
            "shg_member": b.shg_member,
            "prior_subsidy": b.prior_subsidy.value,
            "credit_default": b.credit_default.value,
            "existing_emi_monthly": b.existing_emi_monthly,
            "active_consent": True,
        }
        for b in beneficiaries
    ]


@router.get("/{beneficiary_id}", response_model=BeneficiaryOut)
async def get_beneficiary(
    beneficiary_id: int,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Retrieve single beneficiary details."""
    res = await db.execute(
        select(Beneficiary).where(
            Beneficiary.id == beneficiary_id,
            Beneficiary.org_id == user.org_id,
            Beneficiary.deleted_at.is_(None),
        )
    )
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    await log_processing(
        db=db,
        actor_id=user.id,
        purpose="View beneficiary profile",
        entity="beneficiaries",
        entity_id=str(b.id),
    )
    await db.commit()

    return {
        "id": b.id,
        "org_id": b.org_id,
        "first_name": b.first_name,
        "gender": b.gender,
        "age": b.age,
        "category": b.category,
        "category_verified": b.category_verified,
        "disability_40": b.disability_40,
        "occupation_flags": b.occupation_flags,
        "income_band": b.income_band,
        "education_band": b.education_band,
        "shg_member": b.shg_member,
        "prior_subsidy": b.prior_subsidy.value,
        "credit_default": b.credit_default.value,
        "existing_emi_monthly": b.existing_emi_monthly,
        "active_consent": True,
    }


@router.post("/{beneficiary_id}/consent")
async def record_consent(
    beneficiary_id: int,
    req: ConsentCreate,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Upload or renew consent record (voice audio hash or digital tap)."""
    res = await db.execute(
        select(Beneficiary).where(Beneficiary.id == beneficiary_id, Beneficiary.org_id == user.org_id)
    )
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    consent = Consent(
        beneficiary_id=b.id,
        notice_version=req.notice_version,
        language=req.language,
        method=req.method,
        audio_sha256=req.audio_sha256,
        audio_object_key=req.audio_object_key,
        agent_id=user.id,
    )
    db.add(consent)

    await log_audit(
        db=db,
        actor_id=user.id,
        action="RECORD_CONSENT",
        entity="consents",
        entity_id=str(b.id),
        diff={"method": req.method.value, "version": req.notice_version},
    )
    await db.commit()

    return {
        "status": "success",
        "beneficiary_id": b.id,
        "notice_version": req.notice_version,
        "method": req.method.value,
        "granted_at": consent.granted_at,
    }


@router.post("/{beneficiary_id}/deletion")
async def request_deletion(
    beneficiary_id: int,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """File a DPDP right-to-erasure deletion request for a beneficiary."""
    res = await db.execute(
        select(Beneficiary).where(Beneficiary.id == beneficiary_id, Beneficiary.org_id == user.org_id)
    )
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")

    del_req = DeletionRequest(
        beneficiary_id=b.id,
        by=user.id,
    )
    db.add(del_req)

    await log_audit(
        db=db,
        actor_id=user.id,
        action="REQUEST_DELETION",
        entity="deletion_requests",
        entity_id=str(b.id),
    )
    await db.commit()

    return {
        "status": "deletion_requested",
        "beneficiary_id": b.id,
        "request_id": del_req.id,
        "message": "Deletion request lodged under DPDP Act; will be processed within statutory period.",
    }
