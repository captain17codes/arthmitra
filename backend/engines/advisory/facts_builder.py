from __future__ import annotations

import re
from typing import Any

from .models import EvaluationFacts, FactItem


def _to_float(val: Any) -> float | None:
    """Safely convert various numeric formats to float."""
    if val is None:
        return None
    try:
        clean = re.sub(r"[^\d.-]", "", str(val))
        return float(clean) if clean else None
    except (ValueError, TypeError):
        return None


def build_evaluation_facts(
    case_id: int,
    eval_output: dict[str, Any],
    input_snapshot: dict[str, Any],
    language: str = "mr",
) -> EvaluationFacts:
    """
    Extract factual numbers, confidence ratings, and labels from an evaluation snapshot.
    Strictly grounds the LLM per TECH_SPEC §7.1.
    """
    facts_list: list[FactItem] = []
    allowed_numbers_set: set[float] = set()

    summary = eval_output.get("summary", {})
    viability = eval_output.get("viability", {})
    market = eval_output.get("market", {})
    inputs = input_snapshot.get("inputs", {})

    def add_fact(fact_id: str, label: str, val: Any, unit: str = "", conf: str = "high"):
        facts_list.append(
            FactItem(
                id=fact_id,
                label=label,
                value=val,
                unit=unit,
                confidence=conf,
            )
        )
        f_val = _to_float(val)
        if f_val is not None:
            allowed_numbers_set.add(round(f_val, 2))
            allowed_numbers_set.add(round(f_val, 0))

    # 1. Project & Financing
    add_fact("F01", "Project Cost", summary.get("project_cost", "0"), "INR")
    add_fact("F02", "Own Margin Available", summary.get("margin_available", "0"), "INR")

    top_pkgs = summary.get("top_packages", [])
    if top_pkgs:
        p0 = top_pkgs[0]
        add_fact("F03", "Recommended Scheme", p0.get("scheme_code", ""))
        add_fact("F04", "Loan Amount", p0.get("loan_amount", "0"), "INR")
        add_fact("F05", "Subsidy Amount", p0.get("subsidy_amount", "0"), "INR")
        add_fact("F06", "Own Margin Required", p0.get("own_margin_required", "0"), "INR")
        add_fact("F07", "Annual Interest Rate", p0.get("annual_rate_pct", "0"), "%")
        add_fact("F08", "Repayment Tenure", p0.get("tenure_months", 0), "months")
        add_fact("F09", "Moratorium Period", p0.get("moratorium_months", 0), "months")
        add_fact("F10", "Monthly EMI", p0.get("monthly_emi", "0"), "INR/month")
        add_fact("F11", "Total Repayment", p0.get("total_repayment", "0"), "INR")

    # 2. Viability Metrics
    add_fact("F12", "Average DSCR", summary.get("average_dscr", "0"), "ratio")
    add_fact("F13", "Break-Even Capacity", summary.get("breakeven_capacity_pct", "0"), "%")
    if "dscr_target" in viability:
        add_fact("V01", "DSCR Target", viability.get("dscr_target", "1.25"), "ratio")

    nayak = summary.get("nayak_working_capital", {})
    add_fact("F14", "Nayak Total Working Capital", nayak.get("total", "0"), "INR")
    add_fact("F15", "Nayak Bank Working Capital", nayak.get("bank_finance_20", "0"), "INR")
    add_fact("F16", "Nayak Promoter WC Margin", nayak.get("promoter_margin_5", "0"), "INR")

    udhar = summary.get("udhar_stress", {})
    add_fact("F17", "Udhar Stress Extra WC", udhar.get("extra_wc_needed", "0"), "INR")
    add_fact("F18", "Udhar Cash Buffer", udhar.get("cash_buffer_months", "0"), "months")

    # 3. Market Metrics
    add_fact("F19", "Market Saturation Level", summary.get("market_saturation", "medium"))
    add_fact("F20", "Catchment Population", summary.get("effective_catchment_population", "0"), "persons")
    add_fact("F21", "Monthly Category Demand", summary.get("monthly_category_demand", "0"), "INR/month")
    add_fact("F22", "Reported Competitors", summary.get("competitors_reported", "0"), "shops")

    pop_now = market.get("population_now", {})
    if "value" in pop_now:
        add_fact("F23", "Projected Village Population", pop_now["value"], "persons")

    d_per_shop = market.get("demand_per_shop_monthly", {})
    if "value" in d_per_shop:
        add_fact("F24", "Monthly Demand Per Shop", d_per_shop["value"], "INR/month/shop")

    be_share = market.get("be_market_share", {})
    if "value" in be_share:
        add_fact("F25", "Break-Even Market Share", be_share["value"], "ratio")

    # 4. Calibration & Beneficiary Inputs
    for k, v in inputs.items():
        add_fact(f"INP_{k}", f"Input: {k}", v)

    # 5. Beneficiary age, category
    b_snap = input_snapshot.get("beneficiary", {})
    add_fact("B01", "Beneficiary Age", b_snap.get("age", 0), "years")
    add_fact("B02", "Beneficiary Category", b_snap.get("category", "General"))
    add_fact("B03", "Existing Monthly EMI", b_snap.get("existing_emi", "0"), "INR/month")

    # 6. Add common structural integers (1 to 12 for months, year counts, etc.)
    for standard_int in range(1, 13):
        allowed_numbers_set.add(float(standard_int))
    # 5 years
    allowed_numbers_set.add(5.0)
    # Common percentages if applicable
    allowed_numbers_set.add(100.0)
    allowed_numbers_set.add(20.0)
    allowed_numbers_set.add(25.0)
    allowed_numbers_set.add(5.0)

    # Convert sorted set to list
    allowed_numbers = sorted(list(allowed_numbers_set))

    return EvaluationFacts(
        case_id=case_id,
        business_code=summary.get("business_code", ""),
        business_name={
            "en": summary.get("business_name_en", ""),
            "mr": summary.get("business_name_mr", ""),
        },
        village_name=summary.get("village_name", ""),
        language=language,
        facts=facts_list,
        allowed_numbers=allowed_numbers,
    )
