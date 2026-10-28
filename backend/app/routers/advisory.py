from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from engines.advisory.generator import PROMPT_VERSION, generate_advisory_for_evaluation
from models.case import Advisory, Case, Evaluation

from ..deps import CurrentUser, DbSession, log_audit, log_processing

router = APIRouter(prefix="/evaluations", tags=["Advisory"])


@router.post("/{evaluation_id}/advisory")
async def generate_advisory(
    evaluation_id: int,
    user: CurrentUser,
    db: DbSession,
    language: str = "mr",
) -> dict[str, Any]:
    """
    Generate an AI-assisted advisory report for a completed evaluation.
    Enforces strict facts-grounding and number validation before saving.
    """
    res = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.case).selectinload(Case.beneficiary))
        .where(Evaluation.id == evaluation_id)
    )
    ev = res.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation record not found")

    # Enforce organization boundary
    if ev.case.beneficiary.org_id != user.org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation record not found")

    advisory_output, validator_passed, model_source = await generate_advisory_for_evaluation(
        case_id=ev.case_id,
        eval_output=ev.output,
        input_snapshot=ev.input_snapshot,
        language=language,
    )

    advisory_rec = Advisory(
        evaluation_id=ev.id,
        language=language,
        model=model_source,
        prompt_version=PROMPT_VERSION,
        output=advisory_output.model_dump(),
        validator_passed=validator_passed,
    )
    db.add(advisory_rec)

    await log_audit(
        db=db,
        actor_id=user.id,
        action="GENERATE_ADVISORY",
        entity="advisories",
        entity_id=str(ev.id),
        diff={"model": model_source, "validator_passed": validator_passed},
    )
    await log_processing(
        db=db,
        actor_id=user.id,
        purpose="Generate tailored business advisory report",
        entity="advisories",
        entity_id=str(ev.id),
    )

    await db.commit()
    await db.refresh(advisory_rec)

    return {
        "advisory_id": advisory_rec.id,
        "evaluation_id": ev.id,
        "model": advisory_rec.model,
        "prompt_version": advisory_rec.prompt_version,
        "validator_passed": advisory_rec.validator_passed,
        "output": advisory_rec.output,
        "created_at": advisory_rec.created_at,
    }


@router.get("/{evaluation_id}/advisory")
async def get_advisory(
    evaluation_id: int,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Retrieve existing advisory for an evaluation."""
    res = await db.execute(
        select(Advisory)
        .options(selectinload(Advisory.evaluation).selectinload(Evaluation.case).selectinload(Case.beneficiary))
        .where(Advisory.evaluation_id == evaluation_id)
        .order_by(Advisory.created_at.desc(), Advisory.id.desc())
        .limit(1)
    )
    adv = res.scalars().first()
    if not adv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advisory report not found")

    if adv.evaluation.case.beneficiary.org_id != user.org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advisory report not found")

    return {
        "advisory_id": adv.id,
        "evaluation_id": adv.evaluation_id,
        "model": adv.model,
        "prompt_version": adv.prompt_version,
        "validator_passed": adv.validator_passed,
        "output": adv.output,
        "created_at": adv.created_at,
    }
