"""
Case evaluation service: rules → per-scheme sizing → finance → viability → market.

Invariants (PLAN.md §0):
- Every number comes from the deterministic engines; nothing is invented here.
- Scheme terms come from data/schemes/*.yaml; nothing scheme-specific is hard-coded.
- Unknown facts produce NEEDS_INFO, never a guessed value.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from engines.finance.amortization import generate_schedule, round_curr
from engines.finance.models import (
    FinanceInput,
    FinanceResult,
    InterestSlab,
    MoratoriumMode,
    SubsidyConfig,
    SubsidyTreatment,
)
from engines.finance.sizing import SizingResult, size_project_and_loan
from engines.market.calculator import evaluate_market
from engines.market.models import MarketInput, NeighbourInput
from engines.rules.evaluator import EligibilityStatus, evaluate_scheme, is_special_for_scheme
from engines.rules.models import InterestConfig, SchemeDefinition
from engines.viability.calculator import evaluate_viability
from engines.viability.models import ViabilityInput

ENGINE_VERSION = "1.1.0"

# Years of schooling for each education option the UI/API may send.
EDUCATION_YEARS: dict[str, int] = {
    "illiterate": 0,
    "below_7th": 4,
    "primary": 5,
    "7th_pass": 7,
    "middle_8th": 8,
    "8th_pass": 8,
    "class_8_pass": 8,
    "secondary_10th": 10,
    "10th_pass": 10,
    "class_10_pass": 10,
    "higher_secondary_12th": 12,
    "12th_pass": 12,
    "class_12_pass": 12,
    "graduate": 15,
}

# Legacy income bands → conservative UPPER bound (never under-state income).
# "above_3_lakh" cannot be resolved against ₹5 L / ₹8 L ceilings → unknown.
INCOME_BAND_UPPER: dict[str, int | None] = {
    "below_1_lakh": 100000,
    "1_to_3_lakh": 300000,
    "above_3_lakh": None,
}

# Share of local category demand above which projected revenue is implausible.
MAX_PLAUSIBLE_DEMAND_SHARE = Decimal("0.30")

D0 = Decimal("0")


# ---------------------------------------------------------------------------
# Facts
# ---------------------------------------------------------------------------

def resolve_income(annual_family_income: int | None, income_band: str | None) -> int | None:
    if annual_family_income is not None and annual_family_income >= 0:
        return int(annual_family_income)
    if income_band:
        return INCOME_BAND_UPPER.get(income_band)
    return None


def build_base_facts(beneficiary: Any, case: Any, business_sector: str | None) -> dict[str, Any]:
    """Facts that do not depend on the scheme (project_cost is added per scheme)."""

    def _enum(v: Any) -> Any:
        return v.value if hasattr(v, "value") else v

    occupation = [str(o).lower() for o in (beneficiary.occupation_flags or [])]
    # LIDCOM needs a leather (Charmakar) artisan; a generic "traditional artisan" tick is not enough to decide.
    if "leather_artisan" in occupation:
        leather: bool | None = True
    elif "traditional_artisan" in occupation:
        leather = None
    else:
        leather = False

    return {
        "occupation_flag_safai": "sanitation_worker" in occupation,
        "traditional_artisan_leather": leather,
        "street_vendor": "street_vendor" in occupation,
        "category": beneficiary.category,
        "gender": (beneficiary.gender or "").lower() or None,
        "age": beneficiary.age,
        "disability_40": bool(beneficiary.disability_40),
        "occupation": beneficiary.occupation_flags or [],
        "education_years": EDUCATION_YEARS.get(beneficiary.education_band or ""),
        "shg_member": bool(beneficiary.shg_member),
        "prior_subsidy": _enum(beneficiary.prior_subsidy),
        "credit_default": _enum(beneficiary.credit_default),
        "annual_family_income": resolve_income(
            getattr(beneficiary, "annual_family_income", None), beneficiary.income_band
        ),
        "area_type": "rural",  # v1 serves rural villages from the LGD village list
        "state": "Maharashtra",
        "business_type": case.business_code,
        "business_sector": business_sector,
        "is_new_enterprise": True,  # v1 only plans new units
    }


# ---------------------------------------------------------------------------
# Per-scheme sizing and finance
# ---------------------------------------------------------------------------

@dataclass
class SchemeSizing:
    is_special: bool
    own_share: Decimal
    loan_share: Decimal
    max_project: Decimal | None
    sizing: SizingResult
    subsidy_amount: Decimal
    subsidy_rate: Decimal
    warnings: list[str] = field(default_factory=list)


def _scheme_max_project(sc: SchemeDefinition, sector: str | None) -> Decimal | None:
    fin = sc.finance
    if fin.max_project_cost_by_sector and sector and sector in fin.max_project_cost_by_sector:
        return Decimal(str(fin.max_project_cost_by_sector[sector]))
    return Decimal(str(fin.max_project_cost)) if fin.max_project_cost else None


def size_for_scheme(
    sc: SchemeDefinition,
    facts: dict[str, Any],
    margin: Decimal,
    target: Decimal | None,
    viable_range: dict[str, Any] | None,
    business_name: str | None,
) -> SchemeSizing:
    fin = sc.finance
    special = is_special_for_scheme(sc, facts)
    own_share = Decimal(str(fin.min_own_share))
    if special and fin.min_own_share_special is not None:
        own_share = Decimal(str(fin.min_own_share_special))
    loan_share = (Decimal("1") - own_share) if fin.loan_share_is_remainder else Decimal(str(fin.loan_share))
    max_project = _scheme_max_project(sc, facts.get("business_sector"))
    loan_cap = Decimal(str(fin.loan_cap)) if fin.loan_cap else None
    warnings: list[str] = []

    vmin = Decimal(str(viable_range["min"])) if viable_range and viable_range.get("min") else None
    vmax = Decimal(str(viable_range["max"])) if viable_range and viable_range.get("max") else None

    if own_share <= D0 and (target is None or target <= D0):
        # No own money needed (e.g. MUDRA Shishu): plan at the scheme maximum.
        target_for_sizing = max_project
        warnings.append("No own contribution required; project planned at the scheme maximum.")
    else:
        target_for_sizing = target

    sizing = size_project_and_loan(
        margin_available=margin,
        min_own_share=own_share if own_share > D0 else Decimal("0.0001"),
        loan_share=loan_share,
        max_project_cost=max_project,
        loan_cap=loan_cap,
        target_project_cost=target_for_sizing,
        min_viable_cost=vmin,
        max_viable_cost=vmax,
        business_name=business_name,
    )
    if own_share <= D0:
        sizing.own_margin_required = D0
        sizing.margin_shortfall = D0

    subsidy_amount = D0
    subsidy_rate = D0
    if fin.subsidy and fin.subsidy.rate_by:
        group = "special" if special else "general"
        key = f"{group}_{facts.get('area_type', 'rural')}"
        subsidy_rate = Decimal(str(fin.subsidy.rate_by.get(key, 0)))
        subsidy_amount = round_curr(sizing.project_cost * subsidy_rate)
        if fin.subsidy.cap is not None and subsidy_amount > Decimal(str(fin.subsidy.cap)):
            subsidy_amount = Decimal(str(fin.subsidy.cap))
    if fin.tranches:
        subsidy_amount = sum((Decimal(str(t.grant_amount)) for t in fin.tranches), D0)

    return SchemeSizing(
        is_special=special,
        own_share=own_share,
        loan_share=loan_share,
        max_project=max_project,
        sizing=sizing,
        subsidy_amount=subsidy_amount,
        subsidy_rate=subsidy_rate,
        warnings=warnings + list(sizing.warnings),
    )


def _interest(cfg: InterestConfig) -> tuple[Decimal, list[InterestSlab] | None]:
    slabs = None
    if cfg.type == "slab" and cfg.slabs:
        slabs = [
            InterestSlab(
                upto=Decimal(str(s["upto"])) if s.get("upto") is not None else None,
                rate=Decimal(str(s["rate"])),
            )
            for s in cfg.slabs
        ]
    rate = Decimal(str(cfg.rate)) if cfg.rate is not None else (slabs[0].rate if slabs else D0)
    return rate, slabs


@dataclass
class TrancheResult:
    name: str
    principal: Decimal
    rate: Decimal
    tenure_months: int
    moratorium_months: int
    frequency_months: int
    result: FinanceResult


def finance_for_scheme(sc: SchemeDefinition, ss: SchemeSizing) -> list[TrancheResult]:
    fin = sc.finance
    mode = MoratoriumMode(fin.moratorium_mode_default or "capitalise")
    project = ss.sizing.project_cost
    out: list[TrancheResult] = []

    if fin.tranches:
        for t in fin.tranches:
            principal = round_curr(project * Decimal(str(t.share))) - Decimal(str(t.grant_amount))
            principal = max(principal, D0)
            rate, slabs = _interest(t.interest)
            res = generate_schedule(
                FinanceInput(
                    principal=principal,
                    annual_rate=rate,
                    tenure_months=t.tenure_months,
                    moratorium_months=t.moratorium_months,
                    frequency_months=t.repayment_frequency_months,
                    moratorium_mode=mode,
                    rate_slabs=slabs,
                )
            )
            out.append(
                TrancheResult(t.name, principal, rate, t.tenure_months, t.moratorium_months,
                              t.repayment_frequency_months, res)
            )
        return out

    rate, slabs = _interest(fin.interest)
    subsidy_cfg = None
    if fin.subsidy and ss.subsidy_amount > D0:
        subsidy_cfg = SubsidyConfig(
            amount=ss.subsidy_amount,
            treatment=SubsidyTreatment.FDR_3YR if fin.subsidy.treatment == "fdr_3yr" else SubsidyTreatment.UPFRONT,
            adjust_month=fin.subsidy.adjust_month or 36,
        )
    res = generate_schedule(
        FinanceInput(
            principal=ss.sizing.loan_amount,
            annual_rate=rate,
            tenure_months=fin.tenure_months,
            moratorium_months=fin.moratorium_months,
            frequency_months=fin.repayment_frequency_months,
            moratorium_mode=mode,
            subsidy=subsidy_cfg,
            rate_slabs=slabs,
        )
    )
    out.append(
        TrancheResult("Loan", ss.sizing.loan_amount, res_rate(rate, slabs, ss.sizing.loan_amount),
                      fin.tenure_months, fin.moratorium_months, fin.repayment_frequency_months, res)
    )
    return out


def res_rate(rate: Decimal, slabs: list[InterestSlab] | None, principal: Decimal) -> Decimal:
    if slabs:
        for s in slabs:
            if s.upto is None or principal <= s.upto:
                return s.rate
    return rate


def _s(v: Decimal | None) -> str | None:
    return None if v is None else str(round_curr(v))


def build_package(sc: SchemeDefinition, ss: SchemeSizing, tranches: list[TrancheResult]) -> dict[str, Any]:
    sz = ss.sizing
    # Gross loan: tranche principals exclude the grant part, so add it back for display.
    gross_loan = (sum((t.principal for t in tranches), D0) + ss.subsidy_amount) if sc.finance.tranches else sz.loan_amount
    total_paid = sum((t.result.total_amount_paid for t in tranches), D0)
    # Net cost of finance = everything repaid minus money received. Grants/FDR subsidy make it smaller.
    net_cost = total_paid - gross_loan
    monthly_equiv = sum((t.result.initial_emi / Decimal(t.frequency_months) for t in tranches), D0)
    freq = tranches[0].frequency_months if len({t.frequency_months for t in tranches}) == 1 else 1
    emi = sum((t.result.initial_emi for t in tranches), D0)
    subsequent = None
    if any(t.result.subsequent_emi for t in tranches):
        subsequent = sum(((t.result.subsequent_emi or t.result.initial_emi) for t in tranches), D0)
    return {
        "scheme_code": sc.code,
        "scheme_name": sc.name,
        "agency": sc.agency,
        "scheme_status": sc.status.value,
        "source_url": sc.source.url,
        "source_date": sc.source.date,
        "apply_at": sc.channel.apply_at,
        "documents": sc.documents,
        "notes": sc.notes,
        "indicative_fields": sc.finance.bank_decides,
        "is_special_category": ss.is_special,
        "own_share_pct": _s(ss.own_share * 100),
        "project_cost": _s(sz.project_cost),
        "own_margin_required": _s(sz.own_margin_required),
        "own_margin_available": _s(sz.own_margin_available),
        "margin_shortfall": _s(sz.margin_shortfall),
        "is_affordable": sz.margin_shortfall <= D0,
        "loan_amount": _s(gross_loan),
        "subsidy_amount": _s(ss.subsidy_amount),
        "subsidy_rate_pct": _s(ss.subsidy_rate * 100),
        "subsidy_treatment": (sc.finance.subsidy.treatment if sc.finance.subsidy else
                              ("grant" if sc.finance.tranches else None)),
        "annual_rate_pct": _s(tranches[0].rate * 100),
        "tenure_months": tranches[0].tenure_months,
        "moratorium_months": tranches[0].moratorium_months,
        "emi": _s(emi),
        "emi_frequency_months": freq,
        "monthly_equivalent_emi": _s(monthly_equiv),
        "emi_after_subsidy_adjustment": _s(subsequent),
        "moratorium_interest": _s(sum((t.result.moratorium_interest for t in tranches), D0)),
        "total_repayment": _s(total_paid),
        "net_cost_to_beneficiary": _s(net_cost),
        "net_cost_per_lakh": _s(net_cost / gross_loan * Decimal("100000")) if gross_loan > D0 else "0.00",
        "warnings": ss.warnings,
        "tranches": [
            {
                "name": t.name,
                "principal": _s(t.principal),
                "annual_rate_pct": _s(t.rate * 100),
                "tenure_months": t.tenure_months,
                "moratorium_months": t.moratorium_months,
                "frequency_months": t.frequency_months,
                "emi": _s(t.result.initial_emi),
                "instalments": t.result.num_instalments,
                "schedule": [
                    {
                        "period": r.period,
                        "due_month": r.due_month,
                        "opening_balance": _s(r.opening_balance),
                        "interest": _s(r.interest_payment),
                        "principal": _s(r.principal_payment),
                        "payment": _s(r.total_payment),
                        "subsidy_credit": _s(r.subsidy_credit),
                        "closing_balance": _s(r.closing_balance),
                        "is_moratorium": r.is_moratorium,
                    }
                    for r in t.result.schedule
                ],
            }
            for t in tranches
        ],
    }


def _rank_key(p: dict[str, Any]) -> tuple:
    return (
        0 if p["is_affordable"] else 1,
        Decimal(p["net_cost_per_lakh"]),
        Decimal(p["monthly_equivalent_emi"]),
        p["scheme_code"],
    )


def _annual_debt_service(tranches: list[TrancheResult]) -> tuple[list[Decimal], list[Decimal]]:
    ds = [D0] * 5
    interest = [D0] * 5
    for t in tranches:
        for r in t.result.schedule:
            idx = (r.due_month - 1) // 12
            if 0 <= idx < 5:
                ds[idx] += r.total_payment
                interest[idx] += r.interest_payment
    return ds, interest


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def evaluate(
    *,
    facts: dict[str, Any],
    schemes: dict[str, SchemeDefinition],
    margin: Decimal,
    target: Decimal | None,
    business_code: str,
    business: Any,
    benchmark: dict[str, Any],
    village: Any,
    neighbours: list[NeighbourInput],
    inputs: dict[str, Any],
    existing_monthly_emi: Decimal,
) -> dict[str, Any]:
    eligible: list[tuple[dict[str, Any], list[TrancheResult]]] = []
    not_eligible: list[dict[str, Any]] = []
    needs_info: list[dict[str, Any]] = []
    confirm: list[dict[str, Any]] = []

    for code, sc in sorted(schemes.items()):
        try:
            ss = size_for_scheme(sc, facts, margin, target, benchmark.get("viable_range"), business.name_en)
        except ValueError as e:  # e.g. zero margin with a margin-driven scheme
            not_eligible.append({"code": code, "name": sc.name, "reasons": ["cannot_size_project"], "detail": str(e)})
            continue
        project_for_rules = target if (target is not None and target > D0) else ss.sizing.project_cost
        res = evaluate_scheme(sc, {**facts, "project_cost": float(project_for_rules)})

        if res.status == EligibilityStatus.NOT_ELIGIBLE:
            not_eligible.append({"code": code, "name": sc.name, "reasons": res.reasons})
            continue
        if res.status == EligibilityStatus.NEEDS_INFO:
            needs_info.append({"code": code, "name": sc.name, "missing_fields": res.missing_fields})
            continue

        tranches = finance_for_scheme(sc, ss)
        pkg = build_package(sc, ss, tranches)
        pkg["eligibility_warnings"] = res.warning_messages
        if ss.sizing.margin_shortfall > D0 and target is not None:
            alt = size_for_scheme(sc, facts, margin, None, benchmark.get("viable_range"), business.name_en)
            pkg["affordable_alternative"] = {
                "project_cost": _s(alt.sizing.project_cost),
                "own_margin_required": _s(alt.sizing.own_margin_required),
                "loan_amount": _s(alt.sizing.loan_amount),
            }
        if res.status == EligibilityStatus.CONFIRM_WITH_AGENCY:
            confirm.append(pkg)
        else:
            eligible.append((pkg, tranches))

    eligible.sort(key=lambda x: _rank_key(x[0]))
    for i, (pkg, _) in enumerate(eligible, start=1):
        pkg["rank"] = i
    top = eligible[:3]

    # ---- Viability (only against a real package) ----
    if top:
        lead_pkg, lead_tranches = top[0]
        capex = Decimal(lead_pkg["project_cost"])
        ds, interest = _annual_debt_service(lead_tranches)
        mora = lead_tranches[0].moratorium_months
        monthly_emi = Decimal(lead_pkg["monthly_equivalent_emi"])
        financing_basis = lead_pkg["scheme_code"]
    else:
        vr = benchmark.get("viable_range") or {}
        capex = target if (target and target > D0) else Decimal(str(vr.get("min", margin or 0)))
        ds, interest, mora, monthly_emi = [D0] * 5, [D0] * 5, 0, D0
        financing_basis = None

    income = facts.get("annual_family_income")
    v = evaluate_viability(
        ViabilityInput(
            business_code=business_code,
            capex_total=capex,
            annual_debt_service=ds,
            annual_interest_due=interest,
            calibration_overrides=inputs,
            udhar_pct=Decimal(str(inputs.get("udhar_pct", "0.20"))),
            moratorium_months=mora,
            new_monthly_emi=monthly_emi,
            existing_monthly_emi=existing_monthly_emi,
            household_monthly_income=(Decimal(income) / 12) if income else None,
        ),
        benchmark,
    )

    # ---- Market ----
    competitors_known = inputs.get("competitor_count") not in (None, "")
    m = evaluate_market(
        MarketInput(
            village_lgd=village.lgd_code,
            village_name=village.name_en,
            village_pop_2011=village.pop_2011 or 0,
            district_name=village.district_name,
            business_code=business_code,
            agent_competitor_count=int(inputs.get("competitor_count") or 0),
            neighbours=neighbours,
            be_revenue_monthly=v.breakeven_revenue_yr1 / Decimal("12"),
        )
    )
    market_warnings = list(m.warnings)
    saturation = m.saturation_level.value if competitors_known else "needs_info"
    if not competitors_known:
        market_warnings.insert(0, "Enter the number of similar shops nearby to get a saturation result.")
    if not village.pop_2011:
        market_warnings.insert(0, "Village population is missing; market figures are not reliable.")

    viability_warnings = list(v.warnings)
    yr1_rev = v.projections[0].gross_revenue if v.projections else D0
    demand_month = m.category_demand_monthly.value
    revenue_share = (yr1_rev / 12 / demand_month) if demand_month and demand_month > D0 else None
    if revenue_share is not None and revenue_share > MAX_PLAUSIBLE_DEMAND_SHARE:
        viability_warnings.append(
            f"Projected sales are {revenue_share * 100:.0f}% of all local spending in this category "
            f"(plausible maximum {MAX_PLAUSIBLE_DEMAND_SHARE * 100:.0f}%). Check daily customers/prices with the beneficiary."
        )

    def metric(x: Any) -> dict[str, str]:
        return {"value": str(x.value), "min": str(x.min_value), "max": str(x.max_value)}

    top_pkgs = [p for p, _ in top]
    return {
        "summary": {
            "business_code": business_code,
            "business_name_en": business.name_en,
            "business_name_mr": business.name_mr,
            "village_lgd": village.lgd_code,
            "village_name": village.name_en,
            "project_cost": str(capex),
            "margin_available": str(margin),
            "top_packages": top_pkgs,
            "financing_basis": financing_basis,
            "average_dscr": str(v.average_dscr) if top else None,
            "dscr_passed": v.dscr_passed if top else None,
            "breakeven_capacity_pct": str(v.breakeven_capacity_pct_yr1),
            "nayak_working_capital": {
                "total": str(v.nayak_total_wc),
                "bank_finance_20": str(v.nayak_bank_finance),
                "promoter_margin_5": str(v.nayak_promoter_margin),
            },
            "udhar_stress": {
                "udhar_pct": str(inputs.get("udhar_pct", "0.20")),
                "extra_wc_needed": str(v.udhar_extra_wc_needed),
                "cash_buffer_months": str(v.udhar_cash_buffer_months),
            },
            "market_saturation": saturation,
            "effective_catchment_population": str(m.catchment_population.value),
            "monthly_category_demand": str(m.category_demand_monthly.value),
            "competitors_reported": str(m.competitor_count.value) if competitors_known else None,
        },
        "viability": {
            "dscr_target": str(v.dscr_target),
            "average_dscr": str(v.average_dscr) if top else None,
            "dscr_passed": v.dscr_passed if top else None,
            "income_timing_mismatch": v.income_timing_mismatch,
            "recommended_reserve": str(v.recommended_reserve),
            "foir_pct": str(v.foir_pct) if v.foir_pct is not None else None,
            "foir_passed": v.foir_passed,
            "revenue_share_of_local_demand_pct": str(round_curr(revenue_share * 100)) if revenue_share is not None else None,
            "warnings": viability_warnings,
            "inputs_used": {
                k: ("local" if k in inputs else "default") for k in (benchmark.get("revenue_parameters") or {})
            },
            "projections": [
                {
                    "year": p.year,
                    "capacity_utilization": str(p.capacity_utilization),
                    "gross_revenue": str(p.gross_revenue),
                    "variable_costs": str(p.variable_costs),
                    "fixed_costs": str(p.fixed_costs),
                    "depreciation": str(p.depreciation),
                    "interest": str(p.interest_expense),
                    "pbt": str(p.profit_before_tax),
                    "pat": str(p.profit_after_tax),
                    "cash_accrual": str(p.cash_accrual),
                    "debt_service": str(p.debt_service),
                    "dscr": str(p.dscr) if top else None,
                }
                for p in v.projections
            ],
        },
        "market": {
            "population_now": metric(m.population_now),
            "catchment_population": metric(m.catchment_population),
            "category_demand_monthly": metric(m.category_demand_monthly),
            "competitor_count": metric(m.competitor_count) if competitors_known else None,
            "demand_per_shop_monthly": metric(m.demand_per_shop_monthly) if competitors_known else None,
            "be_market_share": metric(m.be_market_share),
            "saturation_level": saturation,
            "complementary_suggestions": [
                {
                    "business_code": s.business_code,
                    "name_en": s.name_en,
                    "name_mr": s.name_mr,
                    "be_market_share": str(s.be_market_share),
                    "saturation_level": s.saturation_level.value,
                    "monthly_demand": str(s.monthly_demand),
                }
                for s in m.complementary_suggestions
            ],
            "warnings": market_warnings,
            "explanation": m.explanation,
        },
        "rules": {
            "eligible_schemes_count": len(eligible),
            "other_eligible": [p["scheme_code"] for p, _ in eligible[3:]],
            "confirm_with_agency": confirm,
            "needs_info": needs_info,
            "not_eligible": not_eligible,
            # kept for older clients
            "ineligible_schemes": not_eligible,
        },
    }
