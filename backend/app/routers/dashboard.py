from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy import func, select

from models.beneficiary import Beneficiary
from models.case import Case
from models.organization import User

from ..deps import CurrentUser, DbSession

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """Supervisor and Organization analytics dashboard."""
    # Check supervisor role if needed, or allow agents to see org summary
    # 1. Total cases in org
    res_total = await db.execute(
        select(func.count(Case.id))
        .join(Beneficiary)
        .where(Beneficiary.org_id == user.org_id, Beneficiary.deleted_at.is_(None))
    )
    total_cases = res_total.scalar_one() or 0

    # 2. Cases by status
    res_status = await db.execute(
        select(Case.status, func.count(Case.id))
        .join(Beneficiary)
        .where(Beneficiary.org_id == user.org_id, Beneficiary.deleted_at.is_(None))
        .group_by(Case.status)
    )
    by_status = {status_enum.value: count for status_enum, count in res_status.all()}

    # 3. Cases by business type
    res_biz = await db.execute(
        select(Case.business_code, func.count(Case.id))
        .join(Beneficiary)
        .where(Beneficiary.org_id == user.org_id, Beneficiary.deleted_at.is_(None))
        .group_by(Case.business_code)
    )
    by_business = {biz_code: count for biz_code, count in res_biz.all()}

    # 4. Cases per agent
    res_agents = await db.execute(
        select(User.name, func.count(Case.id))
        .join(Case, Case.created_by == User.id)
        .where(User.org_id == user.org_id)
        .group_by(User.id, User.name)
    )
    by_agent = {agent_name: count for agent_name, count in res_agents.all()}

    return {
        "org_id": user.org_id,
        "total_cases": total_cases,
        "cases_by_status": by_status,
        "cases_by_business": by_business,
        "cases_by_agent": by_agent,
    }
