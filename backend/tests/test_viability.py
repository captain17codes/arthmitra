"""
Test suite for Enterprise Viability Engine (Phase 4).
Verifies:
  1. All 10 v1 business benchmarks load and evaluate.
  2. Goatery triggers the income-timing warning (income start at month 12 vs 6m moratorium).
  3. Udhar 40% lowers DSCR in EVERY business.
  4. Nayak Committee working capital calculation (25% total, 20% bank, 5% promoter).
  5. FOIR threshold checks.
"""

from decimal import Decimal

import pytest

from engines.viability import (
    ViabilityInput,
    evaluate_viability,
    load_all_benchmarks,
    load_benchmark,
)

V1_CODES = [
    "dairy",
    "goatery",
    "broiler",
    "kirana",
    "tailoring",
    "beauty_parlour",
    "mobile_repair",
    "flour_mill",
    "papad_pickle",
    "two_wheeler_repair",
]


@pytest.fixture
def all_benchmarks():
    benchmarks = load_all_benchmarks()
    assert len(benchmarks) == 10
    return benchmarks


def test_all_10_benchmarks_load(all_benchmarks):
    """Verify all 10 v1 business YAML files exist and load valid metadata."""
    for code in V1_CODES:
        assert code in all_benchmarks
        b = all_benchmarks[code]
        assert "revenue_parameters" in b
        assert "cost_parameters" in b
        assert "viable_range" in b


def test_goatery_triggers_income_timing_warning():
    """
    CRITICAL ACCEPTANCE CHECK: Goatery must trigger income-timing warning
    because kids reach saleable age at month 12, whereas loan moratorium is 6 months.
    """
    goatery_bench = load_benchmark("goatery")
    assert goatery_bench["income_start_month"] == 12

    input_data = ViabilityInput(
        business_code="goatery",
        capex_total=Decimal("150000"),
        annual_debt_service=[Decimal("36000")] * 5,
        annual_interest_due=[Decimal("12000")] * 5,
        moratorium_months=6,  # 6 months < 12 months!
        new_monthly_emi=Decimal("3000"),
    )

    result = evaluate_viability(input_data, goatery_bench)
    assert result.income_timing_mismatch is True
    assert result.recommended_reserve == Decimal("18000.00")  # (12 - 6) * 3000 = 18000
    assert any("First income expected in month 12" in w for w in result.warnings)


def test_dairy_no_income_timing_warning():
    """Dairy produces income from Month 1, so no timing mismatch with 6m moratorium."""
    dairy_bench = load_benchmark("dairy")
    assert dairy_bench["income_start_month"] == 1

    input_data = ViabilityInput(
        business_code="dairy",
        capex_total=Decimal("200000"),
        annual_debt_service=[Decimal("48000")] * 5,
        annual_interest_due=[Decimal("16000")] * 5,
        moratorium_months=6,
        new_monthly_emi=Decimal("4000"),
    )

    result = evaluate_viability(input_data, dairy_bench)
    assert result.income_timing_mismatch is False
    assert result.recommended_reserve == Decimal("0.00")


@pytest.mark.parametrize("business_code", V1_CODES)
def test_udhar_40_lowers_dscr_in_every_business(all_benchmarks, business_code):
    """
    CRITICAL ACCEPTANCE CHECK: Customer credit (udhar) at 40% must lower DSCR
    in EVERY business compared to low udhar (0% or 10%).
    """
    bench = all_benchmarks[business_code]
    capex = Decimal(str(bench["viable_range"]["min"]))

    debt_service = [Decimal("30000")] * 5
    interest_due = [Decimal("10000")] * 5

    # 1. Low udhar evaluation (0%)
    input_low = ViabilityInput(
        business_code=business_code,
        capex_total=capex,
        annual_debt_service=debt_service,
        annual_interest_due=interest_due,
        udhar_pct=Decimal("0.00"),
        new_monthly_emi=Decimal("2500"),
    )
    res_low = evaluate_viability(input_low, bench)

    # 2. Heavy udhar stress evaluation (40%)
    input_high = ViabilityInput(
        business_code=business_code,
        capex_total=capex,
        annual_debt_service=debt_service,
        annual_interest_due=interest_due,
        udhar_pct=Decimal("0.40"),
        new_monthly_emi=Decimal("2500"),
    )
    res_high = evaluate_viability(input_high, bench)

    # Verify that DSCR is strictly lower under 40% udhar stress
    assert res_high.average_dscr < res_low.average_dscr, (
        f"Udhar 40% did not lower DSCR for {business_code}: "
        f"low={res_low.average_dscr}, high={res_high.average_dscr}"
    )


def test_nayak_committee_working_capital_formula():
    """Verify Nayak Committee 25% total WC, 20% bank finance, 5% promoter margin."""
    bench = load_benchmark("kirana")
    input_data = ViabilityInput(
        business_code="kirana",
        capex_total=Decimal("150000"),
        annual_debt_service=[Decimal("36000")] * 5,
        annual_interest_due=[Decimal("12000")] * 5,
    )
    res = evaluate_viability(input_data, bench)

    yr1_rev = res.projections[0].gross_revenue
    assert res.nayak_total_wc == (yr1_rev * Decimal("0.25")).quantize(Decimal("0.01"))
    assert res.nayak_bank_finance == (yr1_rev * Decimal("0.20")).quantize(Decimal("0.01"))
    assert res.nayak_promoter_margin == (yr1_rev * Decimal("0.05")).quantize(Decimal("0.01"))


def test_foir_limit_check():
    """Verify FOIR warning when EMI exceeds 50% of monthly household income."""
    bench = load_benchmark("tailoring")

    # Pass: 2000 / 10000 = 20%
    input_pass = ViabilityInput(
        business_code="tailoring",
        capex_total=Decimal("50000"),
        annual_debt_service=[Decimal("24000")] * 5,
        annual_interest_due=[Decimal("8000")] * 5,
        new_monthly_emi=Decimal("2000"),
        household_monthly_income=Decimal("10000"),
    )
    res_pass = evaluate_viability(input_pass, bench)
    assert res_pass.foir_passed is True
    assert res_pass.foir_pct == Decimal("20.00")

    # Fail: 6000 / 10000 = 60%
    input_fail = ViabilityInput(
        business_code="tailoring",
        capex_total=Decimal("50000"),
        annual_debt_service=[Decimal("72000")] * 5,
        annual_interest_due=[Decimal("20000")] * 5,
        new_monthly_emi=Decimal("6000"),
        household_monthly_income=Decimal("10000"),
    )
    res_fail = evaluate_viability(input_fail, bench)
    assert res_fail.foir_passed is False
    assert res_fail.foir_pct == Decimal("60.00")
    assert any("exceeds the 50% limit" in w for w in res_fail.warnings)
