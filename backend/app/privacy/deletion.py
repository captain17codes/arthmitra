from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.beneficiary import Beneficiary, Consent
from models.case import Advisory, Case, CaseInput, DprDocument, Evaluation
from models.governance import DeletionRequest

from ..deps import log_audit

logger = logging.getLogger(__name__)


async def execute_beneficiary_deletion(
    db: AsyncSession,
    beneficiary_id: int,
    actor_id: int,
) -> dict[str, Any]:
    """
    Executes DPDP Act statutory right-to-erasure workflow (TECH_SPEC §2 note).
    Actions:
      1. Redacts PII columns on Beneficiary (sets first_name = 'REDACTED', deleted_at = now).
      2. Wipes audio object keys & hashes on Consent (withdrawn_at = now).
      3. Deletes CaseInput transcripts and raw data.
      4. Deletes Advisory LLM outputs.
      5. Deletes DPR generated documents.
      6. Marks DeletionRequest as completed.
      7. Documents action in audit_log.
      8. PRESERVES processing_log (statutory retention without personal content).
    """
    # 1. Fetch Beneficiary
    res_b = await db.execute(select(Beneficiary).where(Beneficiary.id == beneficiary_id))
    b = res_b.scalar_one_or_none()
    if not b:
        raise ValueError(f"Beneficiary {beneficiary_id} not found")

    # 2. Fetch Cases
    res_cases = await db.execute(select(Case).where(Case.beneficiary_id == beneficiary_id))
    cases = res_cases.scalars().all()
    case_ids = [c.id for c in cases]

    deleted_inputs_count = 0
    deleted_advisories_count = 0
    deleted_dprs_count = 0

    if case_ids:
        # Delete CaseInputs
        res_del_inputs = await db.execute(
            delete(CaseInput).where(CaseInput.case_id.in_(case_ids))
        )
        deleted_inputs_count = res_del_inputs.rowcount or 0

        # Fetch Evaluations for these cases
        res_evals = await db.execute(
            select(Evaluation.id).where(Evaluation.case_id.in_(case_ids))
        )
        eval_ids = [row[0] for row in res_evals.all()]

        if eval_ids:
            # Delete Advisories
            res_del_adv = await db.execute(
                delete(Advisory).where(Advisory.evaluation_id.in_(eval_ids))
            )
            deleted_advisories_count = res_del_adv.rowcount or 0

            # Delete DprDocuments
            res_del_dpr = await db.execute(
                delete(DprDocument).where(DprDocument.evaluation_id.in_(eval_ids))
            )
            deleted_dprs_count = res_del_dpr.rowcount or 0

    # 3. Wipe Consent audio & set withdrawn_at
    res_consents = await db.execute(
        select(Consent).where(Consent.beneficiary_id == beneficiary_id)
    )
    consents = res_consents.scalars().all()
    for consent in consents:
        consent.audio_object_key = None
        consent.audio_sha256 = None
        consent.withdrawn_at = func.now()

    # 4. Redact Beneficiary PII
    b.first_name = "REDACTED"
    b.deleted_at = func.now()

    # 5. Complete DeletionRequest if present
    res_req = await db.execute(
        select(DeletionRequest).where(
            DeletionRequest.beneficiary_id == beneficiary_id,
            DeletionRequest.completed_at.is_(None),
        )
    )
    reqs = res_req.scalars().all()
    for req in reqs:
        req.completed_at = func.now()

    # 6. Audit log entry
    await log_audit(
        db=db,
        actor_id=actor_id,
        action="EXECUTE_DELETION",
        entity="beneficiaries",
        entity_id=str(beneficiary_id),
        diff={
            "pii_redacted": True,
            "consents_withdrawn": len(consents),
            "inputs_deleted": deleted_inputs_count,
            "advisories_deleted": deleted_advisories_count,
            "dprs_deleted": deleted_dprs_count,
            "processing_logs_preserved": True,
        },
    )

    await db.commit()

    return {
        "beneficiary_id": beneficiary_id,
        "pii_redacted": True,
        "consents_withdrawn": len(consents),
        "inputs_deleted": deleted_inputs_count,
        "advisories_deleted": deleted_advisories_count,
        "dprs_deleted": deleted_dprs_count,
        "status": "completed",
    }
