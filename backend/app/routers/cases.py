from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from engines.market.models import NeighbourInput
from engines.rules.loader import load_all_schemes
from engines.viability.loader import load_all_benchmarks
from models.beneficiary import Beneficiary
from models.business_type import BusinessType
from models.case import Case, CaseInput, Evaluation
from models.enums import CaseStatus, InputSource
from models.village import Village, VillageNeighbour

from ..deps import CurrentUser, DbSession, log_audit, log_processing
from ..services import evaluation as evaluation_service

router = APIRouter(prefix="/cases", tags=["Cases"])


class CaseCreate(BaseModel):
    beneficiary_id: int
    village_lgd: int
    business_code: str
    margin_available: Decimal = Field(..., ge=0)
    target_project_cost: Decimal | None = None
    language: str = "mr"


class CaseInputPatch(BaseModel):
    inputs: dict[str, Any] = Field(..., description="Key-value calibration inputs")
    source: InputSource = InputSource.AGENT
    transcript: str | None = None


class CaseStatusPatch(BaseModel):
    status: CaseStatus
    status_reason_code: str | None = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_case(
    req: CaseCreate,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Create a new case for an eligible beneficiary in a target village."""
    # 1. Verify beneficiary belongs to user's org & has recorded consent
    res_b = await db.execute(
        select(Beneficiary)
        .options(selectinload(Beneficiary.consents))
        .where(
            Beneficiary.id == req.beneficiary_id,
            Beneficiary.org_id == user.org_id,
            Beneficiary.deleted_at.is_(None),
        )
    )
    b = res_b.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    if not b.consents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create case: Beneficiary lacks required consent record",
        )

    # 2. Verify village & business type
    res_v = await db.execute(select(Village).where(Village.lgd_code == req.village_lgd))
    if not res_v.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Village not found")

    res_bt = await db.execute(select(BusinessType).where(BusinessType.code == req.business_code))
    if not res_bt.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business type not found")

    new_case = Case(
        beneficiary_id=req.beneficiary_id,
        village_lgd=req.village_lgd,
        business_code=req.business_code,
        margin_available=req.margin_available,
        target_project_cost=req.target_project_cost,
        language=req.language,
        status=CaseStatus.DRAFT,
        created_by=user.id,
    )
    db.add(new_case)
    await db.flush()

    await log_audit(
        db=db,
        actor_id=user.id,
        action="CREATE_CASE",
        entity="cases",
        entity_id=str(new_case.id),
        diff={"business_code": req.business_code, "village_lgd": req.village_lgd},
    )
    await db.commit()
    await db.refresh(new_case)

    return {
        "id": new_case.id,
        "beneficiary_id": new_case.beneficiary_id,
        "village_lgd": new_case.village_lgd,
        "business_code": new_case.business_code,
        "margin_available": str(new_case.margin_available),
        "target_project_cost": str(new_case.target_project_cost) if new_case.target_project_cost else None,
        "language": new_case.language,
        "status": new_case.status.value,
        "created_at": new_case.created_at,
    }


@router.get("")
async def list_cases(
    user: CurrentUser,
    db: DbSession,
    status_filter: CaseStatus | None = None,
) -> list[dict[str, Any]]:
    """List all cases created within user's organization."""
    query = (
        select(Case)
        .join(Beneficiary)
        .where(Beneficiary.org_id == user.org_id, Beneficiary.deleted_at.is_(None))
        .order_by(Case.created_at.desc())
    )
    if status_filter:
        query = query.where(Case.status == status_filter)

    res = await db.execute(query)
    cases = res.scalars().all()

    return [
        {
            "id": c.id,
            "beneficiary_id": c.beneficiary_id,
            "village_lgd": c.village_lgd,
            "business_code": c.business_code,
            "margin_available": str(c.margin_available),
            "target_project_cost": str(c.target_project_cost) if c.target_project_cost else None,
            "language": c.language,
            "status": c.status.value,
            "status_reason_code": c.status_reason_code,
            "created_at": c.created_at,
        }
        for c in cases
    ]


@router.get("/{case_id}")
async def get_case(
    case_id: int,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Get single case details including inputs and latest evaluation."""
    res = await db.execute(
        select(Case)
        .options(
            selectinload(Case.beneficiary),
            selectinload(Case.village),
            selectinload(Case.business_type),
            selectinload(Case.inputs),
            selectinload(Case.evaluations),
        )
        .join(Beneficiary)
        .where(
            Case.id == case_id,
            Beneficiary.org_id == user.org_id,
            Beneficiary.deleted_at.is_(None),
        )
    )
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    await log_processing(
        db=db,
        actor_id=user.id,
        purpose="View case file and evaluations",
        entity="cases",
        entity_id=str(c.id),
    )
    await db.commit()

    inputs_dict = {inp.key: inp.value for inp in c.inputs}
    latest_eval = c.evaluations[-1] if c.evaluations else None

    return {
        "id": c.id,
        "beneficiary_id": c.beneficiary_id,
        "beneficiary_name": c.beneficiary.first_name,
        "village_lgd": c.village_lgd,
        "village_name": c.village.name_en if c.village else None,
        "business_code": c.business_code,
        "business_name": c.business_type.name_en if c.business_type else None,
        "margin_available": str(c.margin_available),
        "target_project_cost": str(c.target_project_cost) if c.target_project_cost else None,
        "language": c.language,
        "status": c.status.value,
        "status_reason_code": c.status_reason_code,
        "inputs": inputs_dict,
        "latest_evaluation": (
            {
                "id": latest_eval.id,
                "engine_version": latest_eval.engine_version,
                "created_at": latest_eval.created_at,
                "output": latest_eval.output,
            }
            if latest_eval
            else None
        ),
        "created_at": c.created_at,
    }


@router.patch("/{case_id}/inputs")
async def update_case_inputs(
    case_id: int,
    req: CaseInputPatch,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Save or update calibration inputs for a case."""
    res = await db.execute(
        select(Case)
        .options(selectinload(Case.inputs))
        .join(Beneficiary)
        .where(Case.id == case_id, Beneficiary.org_id == user.org_id)
    )
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    existing_inputs = {inp.key: inp for inp in c.inputs}
    for key, val in req.inputs.items():
        if key in existing_inputs:
            existing_inputs[key].value = val
            existing_inputs[key].source = req.source
            existing_inputs[key].transcript = req.transcript
        else:
            new_input = CaseInput(
                case_id=c.id,
                key=key,
                value=val,
                source=req.source,
                transcript=req.transcript,
            )
            db.add(new_input)

    await log_audit(
        db=db,
        actor_id=user.id,
        action="UPDATE_INPUTS",
        entity="case_inputs",
        entity_id=str(c.id),
        diff={"keys": list(req.inputs.keys())},
    )
    await db.commit()

    return {"status": "inputs_updated", "case_id": c.id, "keys_updated": list(req.inputs.keys())}


@router.patch("/{case_id}/status")
async def update_case_status(
    case_id: int,
    req: CaseStatusPatch,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Update case lifecycle status and record reason code."""
    res = await db.execute(
        select(Case).join(Beneficiary).where(Case.id == case_id, Beneficiary.org_id == user.org_id)
    )
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    old_status = c.status
    c.status = req.status
    c.status_reason_code = req.status_reason_code

    await log_audit(
        db=db,
        actor_id=user.id,
        action="STATUS_CHANGE",
        entity="cases",
        entity_id=str(c.id),
        diff={"from": old_status.value, "to": req.status.value, "reason": req.status_reason_code},
    )
    await db.commit()

    return {
        "status": "status_updated",
        "case_id": c.id,
        "new_status": c.status.value,
        "reason": c.status_reason_code,
    }


class EvaluateRequest(BaseModel):
    """Optional overrides sent with an evaluation (e.g. the udhar slider)."""

    udhar_pct: Decimal | None = Field(default=None, ge=0, le=1)
    inputs: dict[str, Any] | None = None


@router.post("/{case_id}/evaluate")
async def evaluate_case(
    case_id: int,
    user: CurrentUser,
    db: DbSession,
    req: EvaluateRequest | None = None,
) -> dict[str, Any]:
    """
    Run the full evaluation for a case (rules → per-scheme sizing → finance → viability → market)
    and store an immutable snapshot in `evaluations`. See app/services/evaluation.py.
    """
    res = await db.execute(
        select(Case)
        .options(
            selectinload(Case.beneficiary).selectinload(Beneficiary.consents),
            selectinload(Case.village),
            selectinload(Case.business_type),
            selectinload(Case.inputs),
        )
        .join(Beneficiary)
        .where(Case.id == case_id, Beneficiary.org_id == user.org_id, Beneficiary.deleted_at.is_(None))
    )
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    b = c.beneficiary
    if not b.consents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evaluation halted: Active beneficiary consent is missing",
        )

    # Persist any overrides sent with this request so the evaluation is reproducible.
    overrides: dict[str, Any] = dict(req.inputs or {}) if req else {}
    if req and req.udhar_pct is not None:
        overrides["udhar_pct"] = str(req.udhar_pct)
    if overrides:
        existing = {inp.key: inp for inp in c.inputs}
        for key, val in overrides.items():
            if key in existing:
                existing[key].value = val
                existing[key].source = InputSource.AGENT
            else:
                db.add(CaseInput(case_id=c.id, key=key, value=val, source=InputSource.AGENT))
        await db.flush()

    village = c.village
    business = c.business_type
    inputs_dict = {inp.key: inp.value for inp in c.inputs}
    inputs_dict.update(overrides)

    res_neigh = await db.execute(
        select(VillageNeighbour, Village)
        .join(Village, VillageNeighbour.neighbour_lgd == Village.lgd_code)
        .where(VillageNeighbour.lgd_code == village.lgd_code)
    )
    neighbours = [
        NeighbourInput(
            lgd_code=n_vill.lgd_code,
            name_en=n_vill.name_en,
            pop_2011=n_vill.pop_2011 or 0,
            dist_km=float(vn.dist_km),
        )
        for vn, n_vill in res_neigh.all()
    ]

    benchmark = load_all_benchmarks().get(c.business_code)
    if not benchmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark configuration missing for business code '{c.business_code}'",
        )

    sector = getattr(business, "sector", None)
    sector = sector.value if hasattr(sector, "value") else sector
    facts = evaluation_service.build_base_facts(b, c, sector)
    schemes = load_all_schemes()

    eval_payload = evaluation_service.evaluate(
        facts=facts,
        schemes=schemes,
        margin=Decimal(str(c.margin_available)),
        target=Decimal(str(c.target_project_cost)) if c.target_project_cost else None,
        business_code=c.business_code,
        business=business,
        benchmark=benchmark,
        village=village,
        neighbours=neighbours,
        inputs=inputs_dict,
        existing_monthly_emi=Decimal(str(b.existing_emi_monthly or 0)),
    )

    input_snapshot = {
        "case_id": c.id,
        "facts": {k: v for k, v in facts.items() if k != "occupation"},
        "beneficiary": {
            "id": b.id,
            "gender": b.gender,
            "age": b.age,
            "category": b.category,
            "category_verified": bool(b.category_verified),
            "income_band": b.income_band,
            "annual_family_income": facts.get("annual_family_income"),
            "existing_emi": str(b.existing_emi_monthly),
        },
        "village": {
            "lgd_code": village.lgd_code,
            "name": village.name_en,
            "pop_2011": village.pop_2011,
            "neighbours_count": len(neighbours),
        },
        "business_code": c.business_code,
        "margin_available": str(c.margin_available),
        "target_project_cost": str(c.target_project_cost) if c.target_project_cost else None,
        "inputs": inputs_dict,
    }
    evaluation = Evaluation(
        case_id=c.id,
        engine_version=evaluation_service.ENGINE_VERSION,
        scheme_versions={code: {"status": sc.status.value, "source_date": sc.source.date} for code, sc in schemes.items()},
        benchmarks_version="1.0.0",
        input_snapshot=input_snapshot,
        output=eval_payload,
    )
    db.add(evaluation)
    c.status = CaseStatus.READY

    top = eval_payload["summary"]["top_packages"]
    await log_audit(
        db=db,
        actor_id=user.id,
        action="EVALUATE_CASE",
        entity="cases",
        entity_id=str(c.id),
        diff={"top_scheme": top[0]["scheme_code"] if top else "none"},
    )
    await log_processing(
        db=db,
        actor_id=user.id,
        purpose="Run multi-engine evaluation",
        entity="evaluations",
        entity_id=str(c.id),
    )
    await db.commit()
    await db.refresh(evaluation)

    return {
        "evaluation_id": evaluation.id,
        "case_id": c.id,
        "engine_version": evaluation.engine_version,
        "created_at": evaluation.created_at,
        "output": eval_payload,
    }
