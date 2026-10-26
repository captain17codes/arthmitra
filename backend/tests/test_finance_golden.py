"""
Golden test suite for the ArthMitra Finance Engine.
STRICT INVARIANT: Must pass all golden test vectors from TECH_SPEC §4 to ±₹1.00.
Never edit a test vector to make it pass; fix the engine code.
"""

from decimal import Decimal

import pytest

from engines.finance import (
    FinanceInput,
    InterestSlab,
    MoratoriumMode,
    SubsidyConfig,
    SubsidyTreatment,
    generate_schedule,
    round_curr,
    size_project_and_loan,
)


def assert_close(actual: Decimal, expected: Decimal, tolerance: Decimal = Decimal("1.00"), label: str = ""):
    diff = abs(actual - expected)
    assert diff <= tolerance, f"[{label}] Expected {expected}, got {actual} (diff: {diff} exceeds ±₹{tolerance})"


# ==============================================================================
# Golden Vectors from TECH_SPEC §4
# ==============================================================================

def test_golden_vector_1_nsfdc_mfs_capitalise():
    """
    Vector 1: NSFDC MFS, margin ₹10,000, capitalise
    Expected: project 1,00,000; loan 90,000; mor. interest 1,462.50; 11 qtrs; EMI 9,147.23; total 1,00,619.54
    """
    sizing = size_project_and_loan(
        margin_available=Decimal("10000"),
        min_own_share=Decimal("0.10"),
        loan_share=Decimal("0.90"),
        max_project_cost=Decimal("140000"),
        loan_cap=Decimal("125000"),
    )
    assert sizing.project_cost == Decimal("100000")
    assert sizing.loan_amount == Decimal("90000")

    result = generate_schedule(
        FinanceInput(
            principal=sizing.loan_amount,
            annual_rate=Decimal("0.065"),
            tenure_months=36,
            moratorium_months=3,
            frequency_months=3,
            moratorium_mode=MoratoriumMode.CAPITALISE,
        )
    )

    assert_close(result.moratorium_interest, Decimal("1462.50"), Decimal("0.01"), "Moratorium Interest")
    assert result.num_instalments == 11
    assert_close(result.initial_emi, Decimal("9147.23"), Decimal("0.01"), "EMI")
    assert_close(result.total_amount_paid, Decimal("100619.54"), Decimal("1.00"), "Total Paid")


def test_golden_vector_2_nsfdc_mfs_pay():
    """
    Vector 2: NSFDC MFS, margin ₹10,000, pay
    Expected: EMI 9,000.97; total 1,00,473.12
    """
    result = generate_schedule(
        FinanceInput(
            principal=Decimal("90000"),
            annual_rate=Decimal("0.065"),
            tenure_months=36,
            moratorium_months=3,
            frequency_months=3,
            moratorium_mode=MoratoriumMode.PAY,
        )
    )

    assert_close(result.initial_emi, Decimal("9000.97"), Decimal("0.01"), "EMI")
    assert_close(result.total_amount_paid, Decimal("100473.12"), Decimal("1.00"), "Total Paid")


def test_golden_vector_3_nsfdc_mfs_cap():
    """
    Vector 3: NSFDC MFS, margin ₹14,000 (cap)
    Expected: project 1,39,000; loan 1,25,000; EMI 12,704.49
    """
    sizing = size_project_and_loan(
        margin_available=Decimal("14000"),
        min_own_share=Decimal("0.10"),
        loan_share=Decimal("0.90"),
        max_project_cost=Decimal("140000"),
        loan_cap=Decimal("125000"),
    )
    assert sizing.loan_amount == Decimal("125000")
    # Loan + Margin = 1,25,000 + 14,000 = 1,39,000
    assert sizing.project_cost == Decimal("139000")

    result = generate_schedule(
        FinanceInput(
            principal=sizing.loan_amount,
            annual_rate=Decimal("0.065"),
            tenure_months=36,
            moratorium_months=3,
            frequency_months=3,
            moratorium_mode=MoratoriumMode.CAPITALISE,
        )
    )

    assert_close(result.initial_emi, Decimal("12704.49"), Decimal("0.01"), "EMI")


def test_golden_vector_4_nsfdc_tl_capitalise():
    """
    Vector 4: NSFDC TL, margin ₹1,00,000, capitalise
    Expected: project 10,00,000; loan 9,00,000; mor. 36,000; 26 qtrs; EMI 46,518.48; total 12,09,480.48
    """
    sizing = size_project_and_loan(
        margin_available=Decimal("100000"),
        min_own_share=Decimal("0.10"),
        loan_share=Decimal("0.90"),
        max_project_cost=Decimal("5000000"),
        loan_cap=Decimal("4500000"),
    )
    assert sizing.project_cost == Decimal("1000000")
    assert sizing.loan_amount == Decimal("900000")

    result = generate_schedule(
        FinanceInput(
            principal=sizing.loan_amount,
            annual_rate=Decimal("0.08"),
            tenure_months=84,
            moratorium_months=6,
            frequency_months=3,
            moratorium_mode=MoratoriumMode.CAPITALISE,
        )
    )

    assert_close(result.moratorium_interest, Decimal("36000.00"), Decimal("0.01"), "Moratorium Interest")
    assert result.num_instalments == 26
    assert_close(result.initial_emi, Decimal("46518.48"), Decimal("0.01"), "EMI")
    assert_close(result.total_amount_paid, Decimal("1209480.48"), Decimal("1.00"), "Total Paid")


def test_golden_vector_5_nsfdc_tl_pay():
    """
    Vector 5: NSFDC TL, margin ₹1,00,000, pay
    Expected: EMI 44,729.31; total 11,98,962.00
    """
    result = generate_schedule(
        FinanceInput(
            principal=Decimal("900000"),
            annual_rate=Decimal("0.08"),
            tenure_months=84,
            moratorium_months=6,
            frequency_months=3,
            moratorium_mode=MoratoriumMode.PAY,
        )
    )

    assert_close(result.initial_emi, Decimal("44729.31"), Decimal("0.01"), "EMI")
    assert_close(result.total_amount_paid, Decimal("1198962.00"), Decimal("1.00"), "Total Paid")


def test_golden_vector_6_nsfdc_tl_cap():
    """
    Vector 6: NSFDC TL, margin ₹6,00,000
    Expected: capped: project 50,00,000; loan 45,00,000; EMI 2,32,592.40 + warning
    """
    sizing = size_project_and_loan(
        margin_available=Decimal("600000"),
        min_own_share=Decimal("0.10"),
        loan_share=Decimal("0.90"),
        max_project_cost=Decimal("5000000"),
        loan_cap=Decimal("4500000"),
    )
    assert sizing.is_capped is True
    assert sizing.project_cost == Decimal("5000000")
    assert sizing.loan_amount == Decimal("4500000")
    assert len(sizing.warnings) > 0

    result = generate_schedule(
        FinanceInput(
            principal=sizing.loan_amount,
            annual_rate=Decimal("0.08"),
            tenure_months=84,
            moratorium_months=6,
            frequency_months=3,
            moratorium_mode=MoratoriumMode.CAPITALISE,
        )
    )

    assert_close(result.initial_emi, Decimal("232592.40"), Decimal("0.01"), "EMI")


def test_golden_vector_7_pmegp_fdr_subsidy():
    """
    Vector 7: PMEGP, SC, rural, service, project ₹10 L, bank rate 10%, 84 m incl. 6 m mor., monthly, capitalise
    Expected: own 50,000; subsidy 3,50,000 (FDR); loan 9,50,000; mor. 47,500; EMI₁ 17,443.22 (78 m);
              balance at m36 6,87,753.97 → 3,37,753.97 after subsidy; EMI₂ 8,566.31 (48 m); total paid 9,34,479.55
    """
    project_cost = Decimal("1000000")
    own_contribution = Decimal("50000")  # 5% for SC Rural Special
    gross_loan = project_cost - own_contribution  # 9,50,000
    fdr_subsidy = Decimal("350000")  # 35% for Special Rural

    result = generate_schedule(
        FinanceInput(
            principal=gross_loan,
            annual_rate=Decimal("0.10"),
            tenure_months=84,
            moratorium_months=6,
            frequency_months=1,
            moratorium_mode=MoratoriumMode.CAPITALISE,
            subsidy=SubsidyConfig(
                amount=fdr_subsidy,
                treatment=SubsidyTreatment.FDR_3YR,
                adjust_month=36,
            ),
        )
    )

    assert_close(result.moratorium_interest, Decimal("47500.00"), Decimal("0.01"), "Moratorium Interest")
    assert_close(result.initial_emi, Decimal("17443.22"), Decimal("0.01"), "EMI 1")

    # Find row at due_month 36
    m36_row = next(r for r in result.schedule if r.due_month == 36)
    # Balance before subsidy credit was closing_bal + 350000
    bal_before_sub = m36_row.closing_balance + fdr_subsidy
    assert_close(bal_before_sub, Decimal("687753.97"), Decimal("1.00"), "Balance at Month 36 before subsidy")
    assert_close(m36_row.closing_balance, Decimal("337753.97"), Decimal("1.00"), "Balance at Month 36 after subsidy")

    assert result.subsequent_emi is not None
    assert_close(result.subsequent_emi, Decimal("8566.31"), Decimal("0.01"), "EMI 2")
    assert_close(result.total_amount_paid, Decimal("934479.55"), Decimal("1.00"), "Total Paid")


def test_golden_vector_8_mudra_kishor():
    """
    Vector 8: MUDRA Kishor ₹3 L, 11%, 60 m incl. 6 m mor., monthly, capitalise
    Expected: mor. 16,500; EMI 7,457.21; total 4,02,689.38
    """
    result = generate_schedule(
        FinanceInput(
            principal=Decimal("300000"),
            annual_rate=Decimal("0.11"),
            tenure_months=60,
            moratorium_months=6,
            frequency_months=1,
            moratorium_mode=MoratoriumMode.CAPITALISE,
        )
    )

    assert_close(result.moratorium_interest, Decimal("16500.00"), Decimal("0.01"), "Moratorium Interest")
    assert_close(result.initial_emi, Decimal("7457.21"), Decimal("0.01"), "EMI")
    assert_close(result.total_amount_paid, Decimal("402689.38"), Decimal("1.00"), "Total Paid")


# ==============================================================================
# Property Tests
# ==============================================================================

@pytest.mark.parametrize("principal,rate,tenure,mor,freq,mode", [
    (Decimal("100000"), Decimal("0.08"), 36, 0, 1, MoratoriumMode.CAPITALISE),
    (Decimal("250000"), Decimal("0.07"), 60, 6, 1, MoratoriumMode.CAPITALISE),
    (Decimal("500000"), Decimal("0.09"), 84, 6, 3, MoratoriumMode.CAPITALISE),
    (Decimal("150000"), Decimal("0.065"), 36, 3, 3, MoratoriumMode.PAY),
    (Decimal("1000000"), Decimal("0.085"), 60, 12, 1, MoratoriumMode.PAY),
])
def test_property_zero_final_balance(principal, rate, tenure, mor, freq, mode):
    """Property: Final closing balance must always be exactly ₹0.00."""
    result = generate_schedule(
        FinanceInput(
            principal=principal,
            annual_rate=rate,
            tenure_months=tenure,
            moratorium_months=mor,
            frequency_months=freq,
            moratorium_mode=mode,
        )
    )
    last_row = result.schedule[-1]
    assert last_row.closing_balance == Decimal("0.00")


@pytest.mark.parametrize("principal,rate,tenure,mor,freq", [
    (Decimal("100000"), Decimal("0.08"), 36, 0, 1),
    (Decimal("250000"), Decimal("0.07"), 60, 6, 1),
    (Decimal("500000"), Decimal("0.09"), 84, 6, 3),
])
def test_property_sum_of_principal_equals_financed(principal, rate, tenure, mor, freq):
    """Property: Sum of principal payments must equal financed amount (when capitalized)."""
    result = generate_schedule(
        FinanceInput(
            principal=principal,
            annual_rate=rate,
            tenure_months=tenure,
            moratorium_months=mor,
            frequency_months=freq,
            moratorium_mode=MoratoriumMode.CAPITALISE,
        )
    )
    total_principal = sum(row.principal_payment for row in result.schedule)
    assert total_principal == result.financed_principal


def test_property_tenure_monotonicity():
    """Property: Increasing tenure strictly decreases the periodic EMI."""
    emi_36 = generate_schedule(
        FinanceInput(
            principal=Decimal("500000"),
            annual_rate=Decimal("0.08"),
            tenure_months=36,
            moratorium_months=0,
            frequency_months=1,
        )
    ).initial_emi

    emi_60 = generate_schedule(
        FinanceInput(
            principal=Decimal("500000"),
            annual_rate=Decimal("0.08"),
            tenure_months=60,
            moratorium_months=0,
            frequency_months=1,
        )
    ).initial_emi

    emi_84 = generate_schedule(
        FinanceInput(
            principal=Decimal("500000"),
            annual_rate=Decimal("0.08"),
            tenure_months=84,
            moratorium_months=0,
            frequency_months=1,
        )
    ).initial_emi

    assert emi_36 > emi_60 > emi_84


# ==============================================================================
# Edge Cases & Rate Slabs Coverage
# ==============================================================================


def test_edge_zero_moratorium():
    """Test standard amortisation without any moratorium."""
    res = generate_schedule(
        FinanceInput(
            principal=Decimal("50000"),
            annual_rate=Decimal("0.07"),
            tenure_months=12,
            moratorium_months=0,
            frequency_months=1,
        )
    )
    assert res.moratorium_interest == Decimal("0.00")
    assert res.num_instalments == 12
    assert res.schedule[-1].closing_balance == Decimal("0.00")


def test_edge_upfront_subsidy():
    """Test upfront capital subsidy directly reducing loan principal."""
    res = generate_schedule(
        FinanceInput(
            principal=Decimal("100000"),
            annual_rate=Decimal("0.08"),
            tenure_months=24,
            moratorium_months=0,
            frequency_months=1,
            subsidy=SubsidyConfig(
                amount=Decimal("25000"),
                treatment=SubsidyTreatment.UPFRONT,
            ),
        )
    )
    assert res.principal == Decimal("75000")
    assert res.financed_principal == Decimal("75000")


def test_edge_rate_slabs():
    """Test interest rate slabs selection."""
    slabs = [
        InterestSlab(upto=Decimal("50000"), rate=Decimal("0.06")),
        InterestSlab(upto=Decimal("150000"), rate=Decimal("0.07")),
        InterestSlab(upto=None, rate=Decimal("0.08")),
    ]

    # Test slab 1
    res1 = generate_schedule(
        FinanceInput(
            principal=Decimal("40000"),
            annual_rate=Decimal("0.10"),  # fallback
            rate_slabs=slabs,
            tenure_months=12,
        )
    )
    assert res1.schedule[0].interest_payment == round_curr(Decimal("40000") * Decimal("0.06") / Decimal("12"))

    # Test slab 2
    res2 = generate_schedule(
        FinanceInput(
            principal=Decimal("100000"),
            annual_rate=Decimal("0.10"),
            rate_slabs=slabs,
            tenure_months=12,
        )
    )
    assert res2.schedule[0].interest_payment == round_curr(Decimal("100000") * Decimal("0.07") / Decimal("12"))

    # Test slab 3 (above 150000)
    res3 = generate_schedule(
        FinanceInput(
            principal=Decimal("200000"),
            annual_rate=Decimal("0.10"),
            rate_slabs=slabs,
            tenure_months=12,
        )
    )
    assert res3.schedule[0].interest_payment == round_curr(Decimal("200000") * Decimal("0.08") / Decimal("12"))


def test_sizing_target_and_viable_range():
    """Test project sizing with target project cost, shortfall, and viable bounds."""
    # Target with shortfall
    res_short = size_project_and_loan(
        margin_available=Decimal("5000"),
        min_own_share=Decimal("0.10"),
        loan_share=Decimal("0.90"),
        target_project_cost=Decimal("100000"),
    )
    assert res_short.margin_shortfall == Decimal("5000")
    assert any("short of required" in w for w in res_short.warnings)

    # Viable range warnings
    res_range = size_project_and_loan(
        margin_available=Decimal("10000"),
        min_own_share=Decimal("0.10"),
        loan_share=Decimal("0.90"),
        min_viable_cost=Decimal("150000"),
        max_viable_cost=Decimal("300000"),
        business_name="Dairy Farming",
    )
    assert any("lower than typical viable investment" in w for w in res_range.warnings)


def test_invalid_tenure_raises():
    """Tenure less than moratorium must raise ValueError."""
    with pytest.raises(ValueError):
        generate_schedule(
            FinanceInput(
                principal=Decimal("50000"),
                annual_rate=Decimal("0.08"),
                tenure_months=6,
                moratorium_months=6,
            )
        )
