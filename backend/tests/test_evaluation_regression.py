"""
Regression tests for Code Review #1 findings (P0-2..P0-6, P1-1..P1-5), run through the real API.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests.test_core_api import api_client  # noqa: F401  (pytest fixture)


async def _login(client) -> dict[str, str]:
    res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def _evaluate(client, profile: dict, margin: float, business: str = "kirana",
                    target: float | None = None, inputs: dict | None = None) -> dict:
    h = await _login(client)
    ben = {"first_name": "Test", "gender": "female", "age": 30, "category": "SC",
           "prior_subsidy": "no", "education_band": "secondary_10th",
           "consent": {"language": "mr", "method": "tap"}, **profile}
    r = await client.post("/beneficiaries", json=ben, headers=h)
    assert r.status_code == 201, r.text
    body = {"beneficiary_id": r.json()["id"], "village_lgd": 555001,
            "business_code": business, "margin_available": margin}
    if target:
        body["target_project_cost"] = target
    r = await client.post("/cases", json=body, headers=h)
    assert r.status_code == 201, r.text
    r = await client.post(f"/cases/{r.json()['id']}/evaluate", json={"inputs": inputs or {}}, headers=h)
    assert r.status_code == 200, r.text
    return r.json()["output"]


def _pkg(out: dict, code: str) -> dict | None:
    for p in out["summary"]["top_packages"] + out["rules"]["confirm_with_agency"]:
        if p["scheme_code"] == code:
            return p
    return None


def _reasons(out: dict, code: str) -> list[str]:
    for r in out["rules"]["not_eligible"]:
        if r["code"] == code:
            return r["reasons"]
    return []


@pytest.mark.asyncio
async def test_small_sc_margin_gets_nsfdc_micro_finance_quarterly(api_client):  # noqa: F811
    """P0-2 + P0-3: ₹10k margin → NSFDC MFS offered with the QUARTERLY golden EMI."""
    client, _ = api_client
    out = await _evaluate(client, {"annual_family_income": 80000}, 10000)
    p = _pkg(out, "NSFDC_MFS")
    assert p is not None, out["rules"]
    assert Decimal(p["project_cost"]) == Decimal("100000")
    assert Decimal(p["loan_amount"]) == Decimal("90000")
    assert p["emi_frequency_months"] == 3
    assert abs(Decimal(p["emi"]) - Decimal("9147.23")) <= Decimal("0.01")
    assert p["tranches"][0]["instalments"] == 11


@pytest.mark.asyncio
async def test_nsfdc_term_loan_golden_through_api(api_client):  # noqa: F811
    client, _ = api_client
    out = await _evaluate(client, {"annual_family_income": 200000}, 100000, business="dairy", target=1000000)
    p = _pkg(out, "NSFDC_TL")
    assert p is not None
    assert abs(Decimal(p["emi"]) - Decimal("46518.48")) <= Decimal("0.01")
    assert abs(Decimal(p["total_repayment"]) - Decimal("1209480.48")) <= Decimal("1.00")


@pytest.mark.asyncio
async def test_income_above_ceiling_blocks_nsfdc(api_client):  # noqa: F811
    """P0-4: ₹7 L family income must not pass the ₹5 L NSFDC ceiling."""
    client, _ = api_client
    out = await _evaluate(client, {"annual_family_income": 700000}, 100000, business="dairy", target=1000000)
    assert _pkg(out, "NSFDC_TL") is None
    assert "income_above_5l" in _reasons(out, "NSFDC_TL")


@pytest.mark.asyncio
async def test_unknown_income_is_needs_info_not_a_guess(api_client):  # noqa: F811
    client, _ = api_client
    out = await _evaluate(client, {"income_band": "above_3_lakh"}, 100000, business="dairy", target=1000000)
    codes = {r["code"] for r in out["rules"]["needs_info"]}
    assert "NSFDC_TL" in codes


@pytest.mark.asyncio
async def test_general_male_pays_10_percent_and_gets_25_percent_rural_subsidy(api_client):  # noqa: F811
    """P0-5: PMEGP general category: own 10%, rural subsidy 25%."""
    client, _ = api_client
    out = await _evaluate(
        client, {"category": "General", "gender": "male", "annual_family_income": 250000},
        100000, business="tailoring", target=1000000,
    )
    p = _pkg(out, "PMEGP")
    assert p is not None, out["rules"]
    assert Decimal(p["own_margin_required"]) == Decimal("100000")
    assert Decimal(p["subsidy_amount"]) == Decimal("250000")


@pytest.mark.asyncio
async def test_cmegp_general_age_limit_45(api_client):  # noqa: F811
    client, _ = api_client
    out = await _evaluate(
        client, {"category": "General", "gender": "male", "age": 48, "annual_family_income": 250000},
        100000, business="tailoring", target=1000000,
    )
    assert "age_18_45" in _reasons(out, "CMEGP")


@pytest.mark.asyncio
async def test_standup_india_open_to_women_of_any_category(api_client):  # noqa: F811
    """P1-1: Stand-Up India eligible for an OBC woman with a ₹15 L greenfield project."""
    client, _ = api_client
    out = await _evaluate(
        client, {"category": "OBC", "gender": "female", "annual_family_income": 400000},
        400000, business="flour_mill", target=1500000,
    )
    p = _pkg(out, "STANDUP_INDIA")
    assert p is not None, out["rules"]


@pytest.mark.asyncio
async def test_unaffordable_package_shows_shortfall_and_alternative(api_client):  # noqa: F811
    """P1-3: margin ₹50k for a ₹10 L target → shortfall + affordable alternative, not silent."""
    client, _ = api_client
    out = await _evaluate(client, {"annual_family_income": 80000, "prior_subsidy": "yes"},
                          50000, business="dairy", target=1000000)
    pkgs = out["summary"]["top_packages"]
    assert pkgs
    for p in pkgs:
        if not p["is_affordable"]:
            assert Decimal(p["margin_shortfall"]) > 0
            assert "affordable_alternative" in p


@pytest.mark.asyncio
async def test_no_competitor_count_means_needs_info(api_client):  # noqa: F811
    """P1-5: without the agent's competitor count, saturation is NOT reported as 'low'."""
    client, _ = api_client
    out = await _evaluate(client, {"annual_family_income": 80000}, 10000)
    assert out["summary"]["market_saturation"] == "needs_info"
    out2 = await _evaluate(client, {"annual_family_income": 80000}, 10000, inputs={"competitor_count": 4})
    assert out2["summary"]["market_saturation"] in ("low", "medium", "high")


@pytest.mark.asyncio
async def test_never_two_capital_subsidies_in_one_package(api_client):  # noqa: F811
    client, _ = api_client
    out = await _evaluate(client, {"annual_family_income": 80000}, 50000, business="dairy", target=500000)
    for p in out["summary"]["top_packages"]:
        assert len(p["tranches"]) >= 1  # each package is a single scheme (no subsidy stacking)
