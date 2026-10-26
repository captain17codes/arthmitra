from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from engines.finance.amortization import generate_schedule
from engines.finance.models import (
    FinanceInput,
    MoratoriumMode,
    SubsidyConfig,
    SubsidyTreatment,
)
from engines.finance.sizing import size_project_and_loan
from engines.market.calculator import evaluate_market
from engines.market.models import MarketInput, NeighbourInput
from engines.rules.evaluator import EligibilityStatus, evaluate_scheme
from engines.rules.loader import load_all_schemes
from engines.rules.ranking import RankedPackage, rank_packages
from engines.viability.calculator import evaluate_viability
from engines.viability.loader import load_all_benchmarks
from engines.viability.models import ViabilityInput
from models.beneficiary import Beneficiary
from models.business_type import BusinessType
from models.case import Case, CaseInput, Evaluation
from models.enums import CaseStatus, InputSource
from models.village import Village, VillageNeighbour

from ..deps import CurrentUser, DbSession, log_audit, log_processing

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


@router.post("/{case_id}/evaluate")
async def evaluate_case(
    case_id: int,
    user: CurrentUser,
    db: DbSession,
) -> dict[str, Any]:
    """
    Execute full multi-engine evaluation pipeline for a case:
    1. Rules Engine: scheme eligibility, double subsidy checks, and reasons.
    2. Finance Engine: project sizing, subsidy optimization, and amortization schedules.
    3. Viability Engine: 5-year cash flows, DSCR, BEP, Nayak WC, and Udhar stress test.
    4. Market Engine: spatial distance-decay catchment, category demand, and saturation bands.
    Writes immutable snapshot to evaluations table.
    """
    # 1. Load full case context
    res = await db.execute(
        select(Case)
        .options(
            selectinload(Case.beneficiary).selectinload(Beneficiary.consents),
            selectinload(Case.village),
            selectinload(Case.business_type),
            selectinload(Case.inputs),
        )
        .join(Beneficiary)
        .where(Case.id == case_id, Beneficiary.org_id == user.org_id)
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

    village = c.village
    business = c.business_type
    inputs_dict = {inp.key: inp.value for inp in c.inputs}

    # 2. Fetch neighbouring villages (<= 10 km)
    res_neigh = await db.execute(
        select(VillageNeighbour, Village)
        .join(Village, VillageNeighbour.neighbour_lgd == Village.lgd_code)
        .where(VillageNeighbour.lgd_code == village.lgd_code)
    )
    neighbours: list[NeighbourInput] = []
    for vn, n_vill in res_neigh.all():
        neighbours.append(
            NeighbourInput(
                lgd_code=n_vill.lgd_code,
                name_en=n_vill.name_en,
                pop_2011=n_vill.pop_2011 or 1000,
                dist_km=float(vn.dist_km),
            )
        )

    # 3. Assemble Rules Input
    # 3. Assemble Facts for Rules Evaluator
    income_val = Decimal("150000")
    if b.income_band == "below_1_lakh":
        income_val = Decimal("80000")
    elif b.income_band == "1_to_3_lakh":
        income_val = Decimal("200000")
    elif b.income_band == "above_3_lakh":
        income_val = Decimal("400000")

    facts: dict[str, Any] = {
        "category": b.category,
        "gender": b.gender,
        "age": b.age,
        "disability_40": b.disability_40,
        "occupation": b.occupation_flags or [],
        "education": b.education_band,
        "shg_member": b.shg_member,
        "prior_subsidy": b.prior_subsidy.value if hasattr(b.prior_subsidy, "value") else str(b.prior_subsidy),
        "credit_default": b.credit_default.value if hasattr(b.credit_default, "value") else str(b.credit_default),
        "annual_family_income": float(income_val),
        "area_type": "rural",
        "state": "Maharashtra",
        "business_type": c.business_code,
        "project_cost": float(c.target_project_cost or 150000.0),
        "is_new_enterprise": True,
    }

    # 4. Evaluate all 18 schemes
    all_schemes = load_all_schemes()
    eligible_schemes = []
    ineligible_schemes = []

    for sc_code, sc_def in all_schemes.items():
        eval_res = evaluate_scheme(sc_def, facts)
        if eval_res.status == EligibilityStatus.ELIGIBLE:
            eligible_schemes.append((sc_def, eval_res))
        else:
            ineligible_schemes.append({
                "code": sc_code,
                "name": sc_def.name,
                "reasons": eval_res.reasons,
            })

    # 5. Finance Sizing & Amortization for eligible schemes
    candidate_packages: list[RankedPackage] = []
    available_margin = c.margin_available

    for sc_def, _eval_res in eligible_schemes:
        fin = sc_def.finance
        min_own = Decimal(str(fin.min_own_share))
        loan_share = Decimal(str(fin.loan_share))
        loan_cap = Decimal(str(fin.loan_cap)) if fin.loan_cap else None
        proj_cap = Decimal(str(fin.max_project_cost)) if fin.max_project_cost else None

        sub_share = Decimal("0.00")
        if fin.subsidy:
            sub_share = (
                Decimal("0.35")
                if (facts.get("category") in {"SC", "ST", "OBC"} or facts.get("gender") == "female")
                else Decimal("0.25")
            )

        sizing = size_project_and_loan(
            margin_available=available_margin,
            min_own_share=min_own,
            loan_share=loan_share,
            max_project_cost=proj_cap,
            loan_cap=loan_cap,
            target_project_cost=c.target_project_cost,
            upfront_subsidy_share=sub_share,
        )

        annual_rate = (
            Decimal(str(fin.interest.rate))
            if (fin.interest and fin.interest.rate is not None)
            else Decimal("0.09")
        )
        tenure_m = fin.tenure_months
        mora_m = fin.moratorium_months
        mora_mode = (
            MoratoriumMode(fin.moratorium_mode_default)
            if fin.moratorium_mode_default
            else MoratoriumMode.PAY
        )

        subsidy_cfg = None
        if fin.subsidy and sizing.subsidy_amount > Decimal("0"):
            treatment = (
                SubsidyTreatment.FDR_3YR
                if fin.subsidy.treatment == "fdr_3yr"
                else SubsidyTreatment.UPFRONT
            )
            subsidy_cfg = SubsidyConfig(
                amount=sizing.subsidy_amount,
                treatment=treatment,
                adjust_month=fin.subsidy.adjust_month or 36,
            )

        fin_input = FinanceInput(
            principal=sizing.loan_amount,
            annual_rate=annual_rate,
            tenure_months=tenure_m,
            moratorium_months=mora_m,
            moratorium_mode=mora_mode,
            subsidy=subsidy_cfg,
        )

        sched = generate_schedule(fin_input)
        first_post_mora_emi = sched.initial_emi
        net_cost = sched.total_interest_paid - sizing.subsidy_amount
        is_afford = sizing.own_margin_required <= available_margin

        pkg = RankedPackage(
            scheme_code=sc_def.code,
            scheme_name=sc_def.name,
            project_cost=sizing.project_cost,
            own_margin_required=sizing.own_margin_required,
            own_margin_available=available_margin,
            loan_amount=sizing.loan_amount,
            subsidy_amount=sizing.subsidy_amount,
            annual_rate=annual_rate,
            tenure_months=tenure_m,
            moratorium_months=mora_m,
            emi=first_post_mora_emi,
            total_repayment=sched.total_amount_paid,
            net_cost_to_beneficiary=net_cost,
            channel_reliability_score=0.85,
            is_affordable=is_afford,
        )
        candidate_packages.append(pkg)

    top_3, other_pkgs = rank_packages(candidate_packages, top_n=3)

    if not top_3:
        # Fallback pseudo-package if no scheme was eligible (ensures viability runs)
        lead_project_cost = c.target_project_cost or Decimal("100000")
        lead_emi = Decimal("2000.00")
        annual_debt_service = [Decimal("24000.00")] * 5
        annual_interest_due = [Decimal("8000.00"), Decimal("6500.00"), Decimal("5000.00"), Decimal("3000.00"), Decimal("1000.00")]
        lead_mora = 6
    else:
        top_pkg = top_3[0]
        lead_project_cost = top_pkg.project_cost
        lead_emi = top_pkg.emi
        lead_mora = top_pkg.moratorium_months

        # Compute Year 1..5 debt service and interest portions from schedule
        fin_lead = FinanceInput(
            principal=top_pkg.loan_amount,
            annual_rate=top_pkg.annual_rate,
            tenure_months=top_pkg.tenure_months,
            moratorium_months=top_pkg.moratorium_months,
            moratorium_mode=MoratoriumMode.PAY,
            subsidy=(
                SubsidyConfig(amount=top_pkg.subsidy_amount, treatment=SubsidyTreatment.FDR_3YR, adjust_month=36)
                if top_pkg.subsidy_amount > Decimal("0")
                else None
            ),
        )
        sched_lead = generate_schedule(fin_lead)
        annual_debt_service = [Decimal("0.00")] * 5
        annual_interest_due = [Decimal("0.00")] * 5
        for row in sched_lead.schedule:
            yr_idx = min(4, (row.period - 1) // 12)
            annual_debt_service[yr_idx] += row.total_payment
            annual_interest_due[yr_idx] += row.interest_payment

    # 6. Viability Engine
    v_input = ViabilityInput(
        business_code=c.business_code,
        capex_total=lead_project_cost,
        annual_debt_service=annual_debt_service,
        annual_interest_due=annual_interest_due,
        calibration_overrides=inputs_dict,
        udhar_pct=Decimal(str(inputs_dict.get("udhar_pct", "0.20"))),
        moratorium_months=lead_mora,
        new_monthly_emi=lead_emi,
        existing_monthly_emi=Decimal(str(b.existing_emi_monthly or 0.0)),
    )
    all_benchmarks = load_all_benchmarks()
    bm_data = all_benchmarks.get(c.business_code)
    if not bm_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Benchmark configuration missing for business code '{c.business_code}'",
        )
    v_result = evaluate_viability(v_input, bm_data)

    # 7. Market Engine
    be_monthly = v_result.breakeven_revenue_yr1 / Decimal("12")
    c_agent = int(inputs_dict.get("competitor_count", 1))

    m_input = MarketInput(
        village_lgd=village.lgd_code,
        village_name=village.name_en,
        village_pop_2011=village.pop_2011 or 5000,
        district_name=village.district_name,
        business_code=c.business_code,
        agent_competitor_count=c_agent,
        neighbours=neighbours,
        be_revenue_monthly=be_monthly,
    )
    m_result = evaluate_market(m_input)

    # 8. Assemble Evaluation Output Payload
    eval_payload = {
        "summary": {
            "business_code": c.business_code,
            "business_name_en": business.name_en,
            "business_name_mr": business.name_mr,
            "village_lgd": village.lgd_code,
            "village_name": village.name_en,
            "project_cost": str(lead_project_cost),
            "margin_available": str(available_margin),
            "top_packages": [
                {
                    "rank": p.rank,
                    "scheme_code": p.scheme_code,
                    "scheme_name": p.scheme_name,
                    "project_cost": str(p.project_cost),
                    "loan_amount": str(p.loan_amount),
                    "subsidy_amount": str(p.subsidy_amount),
                    "own_margin_required": str(p.own_margin_required),
                    "annual_rate_pct": str(p.annual_rate),
                    "tenure_months": p.tenure_months,
                    "moratorium_months": p.moratorium_months,
                    "monthly_emi": str(p.emi),
                    "total_repayment": str(p.total_repayment),
                    "net_cost": str(p.net_cost_to_beneficiary),
                }
                for p in top_3
            ],
            "average_dscr": str(v_result.average_dscr),
            "dscr_passed": v_result.dscr_passed,
            "breakeven_capacity_pct": str(v_result.breakeven_capacity_pct_yr1),
            "nayak_working_capital": {
                "total": str(v_result.nayak_total_wc),
                "bank_finance_20": str(v_result.nayak_bank_finance),
                "promoter_margin_5": str(v_result.nayak_promoter_margin),
            },
            "udhar_stress": {
                "extra_wc_needed": str(v_result.udhar_extra_wc_needed),
                "cash_buffer_months": str(v_result.udhar_cash_buffer_months),
            },
            "market_saturation": m_result.saturation_level.value,
            "effective_catchment_population": str(m_result.catchment_population.value),
            "monthly_category_demand": str(m_result.category_demand_monthly.value),
            "competitors_reported": str(m_result.competitor_count.value),
        },
        "viability": {
            "dscr_target": str(v_result.dscr_target),
            "average_dscr": str(v_result.average_dscr),
            "income_timing_mismatch": v_result.income_timing_mismatch,
            "recommended_reserve": str(v_result.recommended_reserve),
            "projections": [
                {
                    "year": p.year,
                    "gross_revenue": str(p.gross_revenue),
                    "variable_costs": str(p.variable_costs),
                    "fixed_costs": str(p.fixed_costs),
                    "depreciation": str(p.depreciation),
                    "interest": str(p.interest_expense),
                    "pbt": str(p.profit_before_tax),
                    "pat": str(p.profit_after_tax),
                    "cash_accrual": str(p.cash_accrual),
                    "debt_service": str(p.debt_service),
                    "dscr": str(p.dscr),
                }
                for p in v_result.projections
            ],
        },
        "market": {
            "population_now": {
                "value": str(m_result.population_now.value),
                "min": str(m_result.population_now.min_value),
                "max": str(m_result.population_now.max_value),
            },
            "catchment_population": {
                "value": str(m_result.catchment_population.value),
                "min": str(m_result.catchment_population.min_value),
                "max": str(m_result.catchment_population.max_value),
            },
            "category_demand_monthly": {
                "value": str(m_result.category_demand_monthly.value),
                "min": str(m_result.category_demand_monthly.min_value),
                "max": str(m_result.category_demand_monthly.max_value),
            },
            "competitor_count": {
                "value": str(m_result.competitor_count.value),
                "min": str(m_result.competitor_count.min_value),
                "max": str(m_result.competitor_count.max_value),
            },
            "demand_per_shop_monthly": {
                "value": str(m_result.demand_per_shop_monthly.value),
                "min": str(m_result.demand_per_shop_monthly.min_value),
                "max": str(m_result.demand_per_shop_monthly.max_value),
            },
            "be_market_share": {
                "value": str(m_result.be_market_share.value),
                "min": str(m_result.be_market_share.min_value),
                "max": str(m_result.be_market_share.max_value),
            },
            "saturation_level": m_result.saturation_level.value,
            "complementary_suggestions": [
                {
                    "business_code": s.business_code,
                    "name_en": s.name_en,
                    "name_mr": s.name_mr,
                    "hces_category": s.hces_category,
                    "be_market_share": str(s.be_market_share),
                    "saturation_level": s.saturation_level.value,
                    "monthly_demand": str(s.monthly_demand),
                }
                for s in m_result.complementary_suggestions
            ],
            "warnings": m_result.warnings,
            "explanation": m_result.explanation,
        },
        "rules": {
            "eligible_schemes_count": len(eligible_schemes),
            "ineligible_schemes": ineligible_schemes,
        },
    }

    # 9. Store evaluation snapshot
    input_snapshot = {
        "case_id": c.id,
        "beneficiary": {
            "id": b.id,
            "gender": b.gender,
            "age": b.age,
            "category": b.category,
            "income_band": b.income_band,
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
        engine_version="1.0.0",
        scheme_versions={"schemes_count": len(all_schemes), "version": "1.0.0"},
        benchmarks_version="1.0.0",
        input_snapshot=input_snapshot,
        output=eval_payload,
    )
    db.add(evaluation)

    # 10. Update case status to READY
    c.status = CaseStatus.READY

    await log_audit(
        db=db,
        actor_id=user.id,
        action="EVALUATE_CASE",
        entity="cases",
        entity_id=str(c.id),
        diff={"top_scheme": top_3[0].scheme_code if top_3 else "none"},
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
