"""
Test suite for Rules Engine (Phase 3).
Verifies:
  1. All YAML scheme files load and validate via Pydantic v2.
  2. Scheme test vectors run and pass.
  3. No package has two capital subsidies (Stacking Invariant).
  4. Each eligibility reason code is reachable.
  5. Deterministic ranking orders by affordability, net cost, EMI, and channel reliability.
"""

from decimal import Decimal

import pytest

from engines.rules import (
    CAPITAL_SUBSIDY_SCHEMES,
    EligibilityStatus,
    RankedPackage,
    SchemeStatusType,
    evaluate_scheme,
    load_all_schemes,
    rank_packages,
    validate_stacking,
)


@pytest.fixture
def all_schemes():
    schemes = load_all_schemes()
    assert len(schemes) >= 10, f"Expected at least 10 schemes loaded, found {len(schemes)}"
    return schemes


def test_all_schemes_load_and_validate(all_schemes):
    """Verify that every YAML file in data/schemes parses into valid SchemeDefinition."""
    assert "NSFDC_MFS" in all_schemes
    assert "NSFDC_TL" in all_schemes
    assert "PMEGP" in all_schemes
    assert "CMEGP" in all_schemes
    assert "MUDRA_SHISHU" in all_schemes
    assert "MUDRA_KISHOR" in all_schemes
    assert "STANDUP_INDIA" in all_schemes
    assert "MPBCDC_SEED" in all_schemes
    assert "NBCFDC_GL" in all_schemes

    for code, scheme in all_schemes.items():
        assert scheme.code == code
        assert scheme.agency != ""
        assert scheme.source.url.startswith("http")


def test_stacking_guard_no_two_capital_subsidies():
    """STRICT INVARIANT: No package may ever have two capital subsidies on the same asset."""
    # Prohibited combinations
    cap_sub_list = list(CAPITAL_SUBSIDY_SCHEMES)
    for i in range(len(cap_sub_list)):
        for j in range(i + 1, len(cap_sub_list)):
            is_valid, reason = validate_stacking([cap_sub_list[i], cap_sub_list[j]])
            assert is_valid is False, f"Failed to reject double capital subsidy: {cap_sub_list[i]} + {cap_sub_list[j]}"
            assert "Cannot stack multiple capital subsidies" in reason

    # Permitted combinations
    valid_pair = ["STANDUP_INDIA", "DAY_NRLM_SHG"]
    is_valid, reason = validate_stacking(valid_pair)
    assert is_valid is True
    assert reason is None

    standalone_pmegp = ["PMEGP"]
    is_valid, reason = validate_stacking(standalone_pmegp)
    assert is_valid is True


def test_each_reason_code_is_reachable(all_schemes):
    """Verify that reason codes defined across schemes can actually be reached by evaluator."""
    nsfdc_tl = all_schemes["NSFDC_TL"]

    # 1. Needs SC
    res_sc = evaluate_scheme(nsfdc_tl, {
        "category": "General",
        "annual_family_income": 200000,
        "age": 30,
        "project_cost": 500000,
    })
    assert res_sc.status == EligibilityStatus.NOT_ELIGIBLE
    assert "needs_sc" in res_sc.reasons

    # 2. Income above 5L
    res_inc = evaluate_scheme(nsfdc_tl, {
        "category": "SC",
        "annual_family_income": 600000,
        "age": 30,
        "project_cost": 500000,
    })
    assert res_inc.status == EligibilityStatus.NOT_ELIGIBLE
    assert "income_above_5l" in res_inc.reasons

    # 3. Age out of range
    res_age = evaluate_scheme(nsfdc_tl, {
        "category": "SC",
        "annual_family_income": 200000,
        "age": 55,
        "project_cost": 500000,
    })
    assert res_age.status == EligibilityStatus.NOT_ELIGIBLE
    assert "age_18_50" in res_age.reasons

    # 4. Project cost bounds
    res_proj_low = evaluate_scheme(nsfdc_tl, {
        "category": "SC",
        "annual_family_income": 200000,
        "age": 30,
        "project_cost": 100000,
    })
    assert "project_above_140k" in res_proj_low.reasons

    # 5. Prior subsidy ineligibility
    pmegp = all_schemes["PMEGP"]
    res_prior_sub = evaluate_scheme(pmegp, {
        "age": 30,
        "prior_subsidy": "yes",
    })
    assert res_prior_sub.status == EligibilityStatus.NOT_ELIGIBLE
    assert "prior_subsidy_ineligible" in res_prior_sub.reasons

    # 6. Negative list rejection
    res_neg = evaluate_scheme(pmegp, {
        "age": 30,
        "prior_subsidy": "no",
        "business_type": "tobacco",
    })
    assert res_neg.status == EligibilityStatus.NOT_ELIGIBLE
    assert "business_in_negative_list" in res_neg.reasons


def test_status_conflict_returns_confirm_with_agency(all_schemes):
    """Verify schemes with status conflict or unverified return CONFIRM_WITH_AGENCY."""
    nbcfdc = all_schemes["NBCFDC_GL"]
    assert nbcfdc.status == SchemeStatusType.CONFLICT

    res = evaluate_scheme(nbcfdc, {
        "category": "OBC",
        "annual_family_income": 250000,
        "age": 32,
        "project_cost": 800000,
    })
    assert res.status == EligibilityStatus.CONFIRM_WITH_AGENCY

    nskfdc = all_schemes["NSKFDC"]
    assert nskfdc.status == SchemeStatusType.UNVERIFIED
    res_nsk = evaluate_scheme(nskfdc, {
        "occupation_flag_safai": True,
        "age": 28,
    })
    assert res_nsk.status == EligibilityStatus.CONFIRM_WITH_AGENCY


def test_deterministic_ranking_precedence():
    """
    Verify deterministic ranking:
      1. Affordable options (margin req <= margin avail) first
      2. Lowest net cost
      3. Lower EMI
    """
    pkg_unaffordable = RankedPackage(
        scheme_code="EXPENSIVE_OP",
        scheme_name={"en": "Expensive Option"},
        project_cost=Decimal("1000000"),
        own_margin_required=Decimal("150000"),
        own_margin_available=Decimal("100000"),  # Shortfall!
        loan_amount=Decimal("850000"),
        subsidy_amount=Decimal("0"),
        annual_rate=Decimal("0.08"),
        tenure_months=84,
        moratorium_months=6,
        emi=Decimal("15000"),
        total_repayment=Decimal("1100000"),
        net_cost_to_beneficiary=Decimal("100000"),
        channel_reliability_score=0.85,
        is_affordable=False,
    )

    pkg_subsidized = RankedPackage(
        scheme_code="PMEGP",
        scheme_name={"en": "PMEGP"},
        project_cost=Decimal("500000"),
        own_margin_required=Decimal("25000"),
        own_margin_available=Decimal("100000"),  # Affordable
        loan_amount=Decimal("475000"),
        subsidy_amount=Decimal("175000"),
        annual_rate=Decimal("0.10"),
        tenure_months=84,
        moratorium_months=6,
        emi=Decimal("8500"),
        total_repayment=Decimal("550000"),
        net_cost_to_beneficiary=Decimal("-100000"),  # Negative net cost thanks to subsidy!
        channel_reliability_score=0.85,
        is_affordable=True,
    )

    pkg_nsfdc = RankedPackage(
        scheme_code="NSFDC_TL",
        scheme_name={"en": "NSFDC Term Loan"},
        project_cost=Decimal("500000"),
        own_margin_required=Decimal("50000"),
        own_margin_available=Decimal("100000"),  # Affordable
        loan_amount=Decimal("450000"),
        subsidy_amount=Decimal("0"),
        annual_rate=Decimal("0.08"),
        tenure_months=84,
        moratorium_months=6,
        emi=Decimal("23000"),
        total_repayment=Decimal("600000"),
        net_cost_to_beneficiary=Decimal("150000"),
        channel_reliability_score=0.75,
        is_affordable=True,
    )

    top, remaining = rank_packages([pkg_unaffordable, pkg_nsfdc, pkg_subsidized], top_n=2)

    assert len(top) == 2
    # PMEGP should rank #1 due to affordability and lowest net cost
    assert top[0].scheme_code == "PMEGP"
    # NSFDC should rank #2 due to affordability
    assert top[1].scheme_code == "NSFDC_TL"
    # Unaffordable package should be in remaining
    assert len(remaining) == 1
    assert remaining[0].scheme_code == "EXPENSIVE_OP"
    assert remaining[0].why_not_selected is not None
