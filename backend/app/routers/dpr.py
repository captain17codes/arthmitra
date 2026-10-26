from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from dpr.renderer import render_dpr_pdf
from models.case import Case, DprDocument, Evaluation

from ..deps import CurrentUser, DbSession, log_audit, log_processing

router = APIRouter(tags=["DPR"])

DPR_STORAGE_DIR = Path("data/dpr_output")


@router.post("/evaluations/{evaluation_id}/dpr")
async def generate_dpr(
    evaluation_id: int,
    user: CurrentUser,
    db: DbSession,
    language: str = "mr",
) -> dict[str, Any]:
    """
    Generate official 12-section bank-ready Detailed Project Report (DPR).
    Renders dual-language: selected language (mr/hi) + English bank appraisal copy.
    """
    res = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.case).selectinload(Case.beneficiary))
        .where(Evaluation.id == evaluation_id)
    )
    ev = res.scalar_one_or_none()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation record not found")

    if ev.case.beneficiary.org_id != user.org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation record not found")

    # Render primary language DPR
    dpr_result = render_dpr_pdf(
        case_id=ev.case_id,
        eval_output=ev.output,
        input_snapshot=ev.input_snapshot,
        output_dir=DPR_STORAGE_DIR,
        language=language,
    )

    doc_rec = DprDocument(
        evaluation_id=ev.id,
        language=language,
        object_key=dpr_result.file_path,
        sha256=dpr_result.file_sha256,
    )
    db.add(doc_rec)

    # Render English copy if requested language is not English
    if language != "en":
        dpr_en = render_dpr_pdf(
            case_id=ev.case_id,
            eval_output=ev.output,
            input_snapshot=ev.input_snapshot,
            output_dir=DPR_STORAGE_DIR,
            language="en",
        )
        doc_en = DprDocument(
            evaluation_id=ev.id,
            language="en",
            object_key=dpr_en.file_path,
            sha256=dpr_en.file_sha256,
        )
        db.add(doc_en)

    await log_audit(
        db=db,
        actor_id=user.id,
        action="GENERATE_DPR",
        entity="dpr_documents",
        entity_id=str(ev.id),
        diff={"sha256": dpr_result.file_sha256, "language": language},
    )
    await log_processing(
        db=db,
        actor_id=user.id,
        purpose="Generate bank-ready DPR PDF report",
        entity="dpr_documents",
        entity_id=str(ev.id),
    )

    await db.commit()
    await db.refresh(doc_rec)

    return {
        "dpr_id": doc_rec.id,
        "evaluation_id": ev.id,
        "language": doc_rec.language,
        "file_path": doc_rec.object_key,
        "file_sha256": doc_rec.sha256,
        "download_url": f"/dpr/{doc_rec.id}/download",
    }


@router.get("/evaluations/{evaluation_id}/dpr")
async def list_dpr_documents(
    evaluation_id: int,
    user: CurrentUser,
    db: DbSession,
) -> list[dict[str, Any]]:
    """List all generated DPR documents for an evaluation."""
    res = await db.execute(
        select(DprDocument)
        .options(selectinload(DprDocument.evaluation).selectinload(Evaluation.case).selectinload(Case.beneficiary))
        .where(DprDocument.evaluation_id == evaluation_id)
        .order_by(DprDocument.created_at.desc())
    )
    docs = res.scalars().all()
    if not docs:
        return []

    # Check org isolation
    if docs[0].evaluation.case.beneficiary.org_id != user.org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DPR documents not found")

    return [
        {
            "id": d.id,
            "evaluation_id": d.evaluation_id,
            "language": d.language,
            "file_sha256": d.sha256,
            "download_url": f"/dpr/{d.id}/download",
            "created_at": d.created_at,
        }
        for d in docs
    ]


@router.get("/dpr/{document_id}/download")
async def download_dpr(
    document_id: int,
    db: DbSession,
) -> FileResponse:
    """Download generated bank-ready DPR PDF."""
    res = await db.execute(select(DprDocument).where(DprDocument.id == document_id))
    doc = res.scalar_one_or_none()
    if not doc or not Path(doc.object_key).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DPR document not found")

    return FileResponse(
        path=doc.object_key,
        media_type="application/pdf",
        filename=Path(doc.object_key).name,
    )
