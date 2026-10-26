"""
Enterprise Viability Calculator Engine.
Strictly implements TECH_SPEC §5 with pure Decimal arithmetic.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from engines.finance.amortization import round_curr

from .models import ViabilityInput, ViabilityResult, YearlyProjection
from .revenue_models import REVENUE_MODELS


def evaluate_viability(
    input_data: ViabilityInput,
    benchmark_data: dict[str, Any],
) -> ViabilityResult:
    """
    Compute comprehensive 5-year financial projections, DSCR, Break-Even Point,
    Nayak Committee working capital, Udhar stress, income-timing check, and FOIR.
    """
    warnings: list[str] = []
    business_code = input_data.business_code

    if business_code not in REVENUE_MODELS:
        raise ValueError(f"No revenue model defined for enterprise code: {business_code}")

    rev_fn = REVENUE_MODELS[business_code]
    rev_params = benchmark_data.get("revenue_parameters", {})
    cost_params = benchmark_data.get("cost_parameters", {})
    calib = input_data.calibration_overrides

    # 1. 100% capacity annual revenue
    base_annual_revenue = round_curr(rev_fn(rev_params, calib))

    # 2. Costs at 100% capacity
    # Variable cost can be given as a share of revenue or specific sum
    var_share = Decimal(str(calib.get(
        "variable_cost_share",
        cost_params.get("fodder_and_feed_share", {}).get("value")
        or cost_params.get("raw_material_share", {}).get("value")
        or cost_params.get("consumables_share", {}).get("value")
        or cost_params.get("cosmetics_consumables_share", {}).get("value")
        or Decimal("0.50")
    )))

    # Fixed monthly costs (rent, power, maintenance)
    fixed_monthly = Decimal("0.00")
    for k, v in cost_params.items():
        if "monthly" in k and isinstance(v, dict) and "value" in v:
            fixed_monthly += Decimal(str(calib.get(k, v["value"])))

    annual_fixed_costs = round_curr(fixed_monthly * Decimal("12"))

    # Depreciation: straight-line on capex
    depreciation_rate = Decimal(str(benchmark_data.get("depreciation_rate", "0.10")))
    annual_depreciation = round_curr(input_data.capex_total * depreciation_rate)

    # Capacity ramp over 5 years
    ramp_list = benchmark_data.get("capacity_ramp", [0.60, 0.70, 0.80, 0.90, 0.90])
    ramp = [Decimal(str(r)) for r in ramp_list]

    projections: list[YearlyProjection] = []
    total_dscr = Decimal("0.00")
    valid_dscr_years = 0

    for yr in range(1, 6):
        cap_util = ramp[yr - 1] if yr <= len(ramp) else ramp[-1]
        gross_rev = round_curr(base_annual_revenue * cap_util)
        var_cost = round_curr(gross_rev * var_share)
        fixed_cost = annual_fixed_costs
        deprec = annual_depreciation

        # Debt service and interest due in year
        ds = input_data.annual_debt_service[yr - 1] if yr <= len(input_data.annual_debt_service) else Decimal("0.00")
        interest_exp = input_data.annual_interest_due[yr - 1] if yr <= len(input_data.annual_interest_due) else Decimal("0.00")

        # PBT and PAT
        pbt = gross_rev - var_cost - fixed_cost - deprec - interest_exp
        tax = round_curr(max(Decimal("0.00"), pbt * Decimal("0.10")))
        pat = pbt - tax
        cash_accrual = pat + deprec

        # DSCR = (PAT + Depreciation + Interest) / Debt Service
        # Udhar stress penalty: uncollected customer credit carries a working capital cost / delay
        udhar_drag = round_curr((gross_rev / Decimal("12")) * input_data.udhar_pct * Decimal("0.10"))
        effective_available = (cash_accrual + interest_exp) - udhar_drag

        if ds > Decimal("0.00"):
            dscr = round_curr(effective_available / ds)
            total_dscr += dscr
            valid_dscr_years += 1
        else:
            dscr = Decimal("0.00")

        projections.append(
            YearlyProjection(
                year=yr,
                capacity_utilization=cap_util,
                gross_revenue=gross_rev,
                variable_costs=var_cost,
                fixed_costs=fixed_cost,
                depreciation=deprec,
                interest_expense=interest_exp,
                profit_before_tax=pbt,
                tax=tax,
                profit_after_tax=pat,
                cash_accrual=cash_accrual,
                debt_service=ds,
                dscr=dscr,
            )
        )

    avg_dscr = round_curr(total_dscr / Decimal(max(1, valid_dscr_years)))

    # 3. Target DSCR (≥ 1.50 for manufacturing, ≥ 1.25 for service/trading/agri_allied)
    sector = benchmark_data.get("sector", "service")
    dscr_target = Decimal("1.50") if sector == "manufacturing" else Decimal("1.25")
    dscr_passed = avg_dscr >= dscr_target
    if not dscr_passed:
        warnings.append(
            f"Average DSCR ({avg_dscr:.2f}) is below target benchmark ({dscr_target:.2f})."
        )

    # 4. Break-even Analysis (Year 1)
    yr1_rev = projections[0].gross_revenue
    yr1_var = projections[0].variable_costs
    contribution_margin = yr1_rev - yr1_var
    if contribution_margin > Decimal("0.00"):
        cm_ratio = contribution_margin / yr1_rev
        bep_revenue = round_curr(annual_fixed_costs / cm_ratio)
        bep_capacity_pct = round_curr((bep_revenue / base_annual_revenue) * Decimal("100"))
    else:
        bep_revenue = Decimal("0.00")
        bep_capacity_pct = Decimal("100.00")

    # 5. Working capital (Nayak Committee formula): 25% of turnover (20% bank, 5% promoter)
    nayak_total_wc = round_curr(yr1_rev * Decimal("0.25"))
    nayak_bank_finance = round_curr(yr1_rev * Decimal("0.20"))
    nayak_promoter_margin = round_curr(yr1_rev * Decimal("0.05"))

    # 6. Udhar stress
    monthly_rev_yr1 = yr1_rev / Decimal("12")
    extra_wc_needed = round_curr(monthly_rev_yr1 * input_data.udhar_pct * input_data.credit_months)

    monthly_cash_accrual = projections[0].cash_accrual / Decimal("12")
    if input_data.new_monthly_emi > Decimal("0.00"):
        udhar_cash_buffer_months = round_curr(
            max(Decimal("0.00"), monthly_cash_accrual / input_data.new_monthly_emi)
        )
    else:
        udhar_cash_buffer_months = Decimal("12.00")

    if udhar_cash_buffer_months < Decimal("3.00") and input_data.new_monthly_emi > Decimal("0"):
        warnings.append(
            f"Customer credit (udhar) stress leaves cash buffer of {udhar_cash_buffer_months:.1f} months, "
            "which is below the safe threshold of 3 months EMI."
        )

    # 7. Income-timing check
    income_start_m = benchmark_data.get("income_start_month", 1)
    income_timing_mismatch = income_start_m > input_data.moratorium_months
    recommended_reserve = Decimal("0.00")

    if income_timing_mismatch:
        months_delay = income_start_m - input_data.moratorium_months
        recommended_reserve = round_curr(Decimal(months_delay) * input_data.new_monthly_emi)
        warnings.append(
            f"First income expected in month {income_start_m}, but loan moratorium ends at month {input_data.moratorium_months}. "
            f"Maintain an emergency reserve of ₹{recommended_reserve:,.2f} ({months_delay} months EMI) or seek a longer moratorium."
        )

    # 8. Seasonality & Lowest Cash Month
    seasonality = benchmark_data.get("seasonality", [1.0] * 12)
    lowest_multiplier = Decimal(str(min(seasonality)))
    lowest_month_idx = seasonality.index(min(seasonality)) + 1
    seasonality_lowest_cash = round_curr(monthly_cash_accrual * lowest_multiplier)

    # 9. FOIR Check
    foir_pct: Decimal | None = None
    foir_passed = True
    if input_data.household_monthly_income and input_data.household_monthly_income > Decimal("0.00"):
        total_monthly_emi = input_data.existing_monthly_emi + input_data.new_monthly_emi
        foir_pct = round_curr((total_monthly_emi / input_data.household_monthly_income) * Decimal("100"))
        foir_passed = foir_pct <= Decimal("50.00")
        if not foir_passed:
            warnings.append(
                f"Total EMI commitment (FOIR {foir_pct:.1f}%) exceeds the 50% limit of household monthly income."
            )

    return ViabilityResult(
        business_code=business_code,
        projections=projections,
        average_dscr=avg_dscr,
        dscr_target=dscr_target,
        dscr_passed=dscr_passed,
        breakeven_revenue_yr1=bep_revenue,
        breakeven_capacity_pct_yr1=bep_capacity_pct,
        nayak_total_wc=nayak_total_wc,
        nayak_bank_finance=nayak_bank_finance,
        nayak_promoter_margin=nayak_promoter_margin,
        udhar_extra_wc_needed=extra_wc_needed,
        udhar_cash_buffer_months=udhar_cash_buffer_months,
        income_timing_mismatch=income_timing_mismatch,
        recommended_reserve=recommended_reserve,
        seasonality_lowest_month_cash=seasonality_lowest_cash,
        seasonality_lowest_month_idx=lowest_month_idx,
        foir_pct=foir_pct,
        foir_passed=foir_passed,
        warnings=warnings,
    )
