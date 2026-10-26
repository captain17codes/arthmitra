"""
Pure Python deterministic Amortization & Repayment Schedule Engine.
Strictly implements TECH_SPEC §4 with Decimal arithmetic.
Zero LLM or floating-point approximations.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from .models import (
    FinanceInput,
    FinanceResult,
    MoratoriumMode,
    ScheduleRow,
    SubsidyTreatment,
)

TWO_PLACES = Decimal("0.01")


def round_curr(amount: Decimal) -> Decimal:
    """Round to 2 decimal places using standard financial half-up rule."""
    return amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def calculate_moratorium_interest(
    principal: Decimal,
    annual_rate: Decimal,
    moratorium_months: int,
) -> Decimal:
    """
    Calculate simple interest accrued during moratorium period.
    Formula: P * r * (m / 12)
    Simple interest; never waived.
    """
    if moratorium_months <= 0 or principal <= Decimal("0"):
        return Decimal("0.00")
    return round_curr(principal * annual_rate * Decimal(moratorium_months) / Decimal("12"))


def calculate_emi(
    principal: Decimal,
    periodic_rate: Decimal,
    num_periods: int,
) -> Decimal:
    """
    Calculate standard equal instalment (EMI / EQI).
    Formula: P * r / (1 - (1 + r)^(-n))
    """
    if num_periods <= 0 or principal <= Decimal("0"):
        return Decimal("0.00")
    if periodic_rate <= Decimal("0"):
        return round_curr(principal / Decimal(num_periods))

    one_plus_r = Decimal("1") + periodic_rate
    # High-precision exponentiation with Decimal
    discount_factor = Decimal("1") - (one_plus_r ** Decimal(-num_periods))
    emi_raw = (principal * periodic_rate) / discount_factor
    return round_curr(emi_raw)


def determine_applicable_rate(input_data: FinanceInput) -> Decimal:
    """Determine the applicable annual interest rate from fixed rate or rate slabs."""
    if input_data.rate_slabs:
        for slab in input_data.rate_slabs:
            if slab.upto is None or input_data.principal <= slab.upto:
                return slab.rate
    return input_data.annual_rate


def generate_schedule(input_data: FinanceInput) -> FinanceResult:
    """
    Generate complete repayment schedule and summary metrics strictly adhering to TECH_SPEC §4.
    """
    warnings: list[str] = []
    annual_rate = determine_applicable_rate(input_data)
    freq = input_data.frequency_months
    tenure_m = input_data.tenure_months
    mor_m = input_data.moratorium_months
    mode = input_data.moratorium_mode
    subsidy = input_data.subsidy

    # 1. Base Loan and Upfront Subsidy
    gross_principal = input_data.principal
    net_principal = gross_principal

    if subsidy and subsidy.treatment == SubsidyTreatment.UPFRONT:
        net_principal = gross_principal - subsidy.amount
        if net_principal < Decimal("0"):
            net_principal = Decimal("0")
            warnings.append("Upfront subsidy exceeds gross loan amount.")

    # 2. Moratorium calculation (simple interest)
    mor_interest = calculate_moratorium_interest(net_principal, annual_rate, mor_m)

    if mode == MoratoriumMode.CAPITALISE:
        financed_principal = net_principal + mor_interest
    else:
        financed_principal = net_principal

    # 3. Periods calculation
    regular_months = tenure_m - mor_m
    if regular_months < freq:
        raise ValueError(f"Tenure ({tenure_m}m) must be greater than moratorium ({mor_m}m) by at least {freq}m.")

    num_instalments = regular_months // freq
    periodic_rate = annual_rate * Decimal(freq) / Decimal("12")

    # 4. Initial EMI computation
    initial_emi = calculate_emi(financed_principal, periodic_rate, num_instalments)
    subsequent_emi: Decimal | None = None

    schedule: list[ScheduleRow] = []
    total_principal_paid = Decimal("0.00")
    total_interest_paid = Decimal("0.00")
    total_amount_paid = Decimal("0.00")

    period_idx = 1

    # 5. Moratorium Rows (when mode is PAY)
    if mode == MoratoriumMode.PAY and mor_m > 0:
        mor_periods = mor_m // freq
        mor_periodic_interest = round_curr(net_principal * periodic_rate)

        for p in range(1, mor_periods + 1):
            due_month = p * freq
            # Last moratorium period absorbs any simple interest rounding
            if p == mor_periods:
                int_pmt = mor_interest - (mor_periodic_interest * Decimal(mor_periods - 1))
            else:
                int_pmt = mor_periodic_interest

            row = ScheduleRow(
                period=period_idx,
                due_month=due_month,
                opening_balance=net_principal,
                interest_payment=int_pmt,
                principal_payment=Decimal("0.00"),
                total_payment=int_pmt,
                closing_balance=net_principal,
                is_moratorium=True,
            )
            schedule.append(row)
            total_interest_paid += int_pmt
            total_amount_paid += int_pmt
            period_idx += 1

    # 6. Regular Amortisation Rows
    current_balance = financed_principal
    current_emi = initial_emi

    for i in range(1, num_instalments + 1):
        due_month = mor_m + (i * freq)
        is_last_instalment = (i == num_instalments)

        interest_pmt = round_curr(current_balance * periodic_rate)

        if is_last_instalment:
            # Last row absorbs fractional rounding (closing balance = 0.00)
            principal_pmt = current_balance
            total_pmt = principal_pmt + interest_pmt
            closing_bal = Decimal("0.00")
        else:
            principal_pmt = current_emi - interest_pmt
            # Guard against edge case where EMI is smaller than interest
            if principal_pmt < Decimal("0"):
                principal_pmt = Decimal("0.00")
            closing_bal = current_balance - principal_pmt
            total_pmt = current_emi

        sub_credit = Decimal("0.00")

        # 7. FDR Subsidy adjustment at adjust_month (e.g. Month 36)
        if subsidy and subsidy.treatment == SubsidyTreatment.FDR_3YR and due_month == subsidy.adjust_month:
            sub_credit = subsidy.amount
            closing_bal = closing_bal - sub_credit
            if closing_bal < Decimal("0"):
                closing_bal = Decimal("0.00")

            # Recompute EMI for remaining instalments
            remaining_instalments = num_instalments - i
            if remaining_instalments > 0 and closing_bal > Decimal("0"):
                current_emi = calculate_emi(closing_bal, periodic_rate, remaining_instalments)
                subsequent_emi = current_emi

        row = ScheduleRow(
            period=period_idx,
            due_month=due_month,
            opening_balance=current_balance,
            interest_payment=interest_pmt,
            principal_payment=principal_pmt,
            total_payment=total_pmt,
            closing_balance=closing_bal,
            is_moratorium=False,
            subsidy_credit=sub_credit,
        )
        schedule.append(row)

        total_principal_paid += principal_pmt
        total_interest_paid += interest_pmt
        total_amount_paid += total_pmt

        current_balance = closing_bal
        period_idx += 1

    # 8. Effective annual cost (annualised interest / principal)
    tenure_years = Decimal(tenure_m) / Decimal("12")
    if net_principal > Decimal("0") and tenure_years > Decimal("0"):
        effective_annual_cost = round_curr(
            (total_interest_paid / net_principal / tenure_years) * Decimal("100")
        )
    else:
        effective_annual_cost = Decimal("0.00")

    return FinanceResult(
        principal=net_principal,
        financed_principal=financed_principal,
        moratorium_interest=mor_interest,
        initial_emi=initial_emi,
        subsequent_emi=subsequent_emi,
        num_instalments=num_instalments,
        total_principal_paid=total_principal_paid,
        total_interest_paid=total_interest_paid,
        total_amount_paid=total_amount_paid,
        effective_annual_cost=effective_annual_cost,
        schedule=schedule,
        warnings=warnings,
    )
