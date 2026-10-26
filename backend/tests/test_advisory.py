from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from adapters.llm import MockLLMAdapter
from app.database import Base, get_db
from app.main import app
from app.security import hash_pin
from app.seed import seed_business_types, seed_schemes
from engines.advisory import (
    build_evaluation_facts,
    extract_numbers_from_text,
    generate_advisory_for_evaluation,
    validate_advisory_numbers,
)
from models.enums import OrgType, UserRole
from models.organization import Organization, User
from models.village import Village


def test_facts_builder_and_number_validator():
    """Verify facts extraction and number validator catching unauthorized numbers."""
    mock_eval_output = {
        "summary": {
            "business_code": "dairy",
            "business_name_en": "Dairy Farming",
            "business_name_mr": "दुग्धव्यवसाय",
            "village_name": "Shirwal",
            "project_cost": "150000.00",
            "margin_available": "15000.00",
            "top_packages": [
                {
                    "scheme_code": "NSFDC_MFS",
                    "loan_amount": "135000.00",
                    "subsidy_amount": "0.00",
                    "own_margin_required": "15000.00",
                    "annual_rate_pct": "6.00",
                    "tenure_months": 36,
                    "moratorium_months": 6,
                    "monthly_emi": "4109.52",
                    "total_repayment": "147942.72",
                }
            ],
            "average_dscr": "2.45",
            "breakeven_capacity_pct": "38.50",
            "nayak_working_capital": {
                "total": "37500.00",
                "bank_finance_20": "30000.00",
                "promoter_margin_5": "7500.00",
            },
            "udhar_stress": {
                "extra_wc_needed": "12000.00",
                "cash_buffer_months": "4.20",
            },
            "market_saturation": "low",
            "effective_catchment_population": "18500",
            "monthly_category_demand": "152000.00",
            "competitors_reported": "2",
        },
        "market": {
            "population_now": {"value": "15500"},
            "demand_per_shop_monthly": {"value": "50666.67"},
            "be_market_share": {"value": "0.18"},
        },
    }

    mock_input_snapshot = {
        "inputs": {"animals": 2, "daily_production_litres": 18, "udhar_pct": 0.20},
        "beneficiary": {"age": 32, "category": "SC", "existing_emi": "0.00"},
    }

    facts = build_evaluation_facts(
        case_id=1,
        eval_output=mock_eval_output,
        input_snapshot=mock_input_snapshot,
        language="mr",
    )

    assert len(facts.facts) >= 15
    assert 150000.0 in facts.allowed_numbers
    assert 135000.0 in facts.allowed_numbers
    assert 2.45 in facts.allowed_numbers

    # 1. Valid advisory containing only permitted numbers
    valid_advisory = {
        "market_reach": "शिरवळ गावात दुग्धव्यवसाय साठी ₹1,50,000 चा प्रकल्प चांगला आहे.",
        "opportunities": ["मासिक हप्ता ₹4,109.52 वेळेत फेडता येईल."],
        "swot": {"s": ["DSCR 2.45 उत्तम आहे."], "w": [], "o": [], "t": []},
        "threats": [],
        "pricing": {"strategy": "वाजवी दर", "items": []},
        "complementary": [],
        "next_steps": ["३६ महिन्यांत कर्ज परतफेड."],
    }
    is_valid, bad_nums = validate_advisory_numbers(valid_advisory, facts.allowed_numbers)
    assert is_valid is True
    assert len(bad_nums) == 0

    # 2. Injected hallucinated number (₹99,999) must be caught by validator
    bad_advisory = {
        "market_reach": "शिरवळ गावात विनापरवाना अंदाज: ₹99,999.00 नफा होईल.",
        "opportunities": [],
        "swot": {"s": [], "w": [], "o": [], "t": []},
        "threats": [],
        "pricing": {"strategy": "", "items": []},
        "complementary": [],
        "next_steps": [],
    }
    is_bad_valid, bad_nums = validate_advisory_numbers(bad_advisory, facts.allowed_numbers)
    assert is_bad_valid is False
    assert 99999.0 in bad_nums


def test_devanagari_numbers_extraction():
    """Verify extraction of numbers written in Devanagari script (e.g. ₹१,५०,०००)."""
    text = "प्रकल्प खर्च ₹१,५०,००० असून मासिक हप्ता ₹४,११० आहे."
    extracted = extract_numbers_from_text(text)
    assert 150000.0 in extracted
    assert 4110.0 in extracted


@pytest.mark.asyncio
async def test_generator_fallback_on_bad_llm():
    """Verify that when an LLM persistently hallucinates numbers, the system safely falls back to template."""
    mock_eval = {
        "summary": {
            "business_code": "kirana",
            "business_name_en": "Kirana Store",
            "business_name_mr": "किराणा दुकान",
            "project_cost": "200000.00",
            "average_dscr": "1.8",
            "top_packages": [
                {
                    "scheme_code": "PMEGP",
                    "loan_amount": "190000.00",
                    "subsidy_amount": "70000.00",
                    "own_margin_required": "10000.00",
                    "monthly_emi": "3200.00",
                }
            ],
            "competitors_reported": "3",
            "market_saturation": "medium",
        },
        "market": {"complementary_suggestions": []},
    }
    mock_snap = {
        "inputs": {},
        "beneficiary": {"age": 28, "category": "General"},
    }

    # Adapter injecting bad numbers
    bad_adapter = MockLLMAdapter(should_inject_bad_number=True)

    output, validator_passed, model_source = await generate_advisory_for_evaluation(
        case_id=99,
        eval_output=mock_eval,
        input_snapshot=mock_snap,
        language="mr",
        adapter=bad_adapter,
    )

    # Must fall back to template
    assert model_source == "template_fallback"
    assert validator_passed is True
    assert output.market_reach != ""
    assert len(output.next_steps) > 0


@pytest.fixture
async def advisory_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session_factory() as session:
        org = Organization(id=1, name="UMED Pune", type=OrgType.NRLM)
        session.add(org)
        await session.flush()

        agent = User(
            id=1,
            org_id=1,
            role=UserRole.AGENT,
            name="Sunita Patil",
            phone="9876543210",
            pin_hash=hash_pin("1234"),
            lang="mr",
        )
        session.add(agent)
        await seed_business_types(session)
        await seed_schemes(session)

        v = Village(lgd_code=555001, name_en="Shirwal", name_mr="शिरवळ", subdistrict_lgd=4201, subdistrict_name="Haveli", district_lgd=490, district_name="Pune", pop_2011=14250)
        session.add(v)
        await session.commit()

    async def override_get_db():
        async with async_session_factory() as session:
            try:
                yield session
            finally:
                pass

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, async_session_factory

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_advisory_api_endpoint(advisory_client):
    """Test POST /evaluations/{id}/advisory and GET /evaluations/{id}/advisory."""
    client, _ = advisory_client

    # 1. Login
    l_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token = l_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Beneficiary + Case + Evaluate
    b_res = await client.post(
        "/beneficiaries",
        json={
            "first_name": "Meena",
            "gender": "female",
            "age": 34,
            "category": "OBC",
            "consent": {"notice_version": "v1.0-2026-04", "method": "voice"},
        },
        headers=headers,
    )
    b_id = b_res.json()["id"]

    c_res = await client.post(
        "/cases",
        json={
            "beneficiary_id": b_id,
            "village_lgd": 555001,
            "business_code": "dairy",
            "margin_available": 15000.0,
            "target_project_cost": 150000.0,
        },
        headers=headers,
    )
    case_id = c_res.json()["id"]

    eval_res = await client.post(f"/cases/{case_id}/evaluate", headers=headers)
    assert eval_res.status_code == 200
    eval_id = eval_res.json()["evaluation_id"]

    # 3. Generate Advisory
    adv_res = await client.post(f"/evaluations/{eval_id}/advisory", headers=headers)
    assert adv_res.status_code == 200
    adv_data = adv_res.json()

    assert adv_data["evaluation_id"] == eval_id
    assert adv_data["validator_passed"] is True
    assert "output" in adv_data
    assert "market_reach" in adv_data["output"]
    assert "swot" in adv_data["output"]
    assert "threats" in adv_data["output"]
    assert "next_steps" in adv_data["output"]

    # 4. Fetch Advisory
    get_adv = await client.get(f"/evaluations/{eval_id}/advisory", headers=headers)
    assert get_adv.status_code == 200
    assert get_adv.json()["advisory_id"] == adv_data["advisory_id"]
