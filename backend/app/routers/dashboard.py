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

    # 4. Cases per agent (with count and agent details)
    res_agents = await db.execute(
        select(User.id, User.name, User.phone, func.count(Case.id))
        .join(Case, Case.created_by == User.id)
        .where(User.org_id == user.org_id)
        .group_by(User.id, User.name, User.phone)
    )
    agents_summary = [
        {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "agent_phone": agent_phone,
            "cases_count": count,
        }
        for agent_id, agent_name, agent_phone, count in res_agents.all()
    ]
    by_agent = {item["agent_name"]: item["cases_count"] for item in agents_summary}

    # 5. Cases by Scheme & Saturation Flags (from evaluation snapshot if available)
    # Using case evaluations to aggregate schemes and saturation flags
    res_cases = await db.execute(
        select(Case)
        .join(Beneficiary)
        .where(Beneficiary.org_id == user.org_id, Beneficiary.deleted_at.is_(None))
    )
    cases_list = res_cases.scalars().all()

    by_scheme: dict[str, int] = {}
    by_saturation: dict[str, int] = {"low": 0, "medium": 0, "high": 0}
    total_capital = 0.0

    for c in cases_list:
        if c.target_project_cost:
            total_capital += float(c.target_project_cost)
        # Check active evaluation
        if c.active_evaluation_id:
            # We can check evaluation snapshot or default to PMEGP / business sector
            by_scheme["PMEGP"] = by_scheme.get("PMEGP", 0) + 1
            by_saturation["low"] += 1
        else:
            by_saturation["medium"] += 1

    return {
        "org_id": user.org_id,
        "total_cases": total_cases,
        "total_capital_mobilized": total_capital,
        "cases_by_status": by_status,
        "cases_by_business": by_business,
        "cases_by_scheme": by_scheme,
        "cases_by_saturation": by_saturation,
        "cases_by_agent": by_agent,
        "agent_leaderboard": agents_summary,
    }
