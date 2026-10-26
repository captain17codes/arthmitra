from __future__ import annotations

from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security import hash_pin
from app.seed import seed_business_types, seed_schemes
from models.enums import OrgType, UserRole
from models.governance import AuditLog, ProcessingLog
from models.organization import Organization, User
from models.village import Village, VillageNeighbour


@pytest.fixture
async def api_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Seed baseline fixtures: 2 Orgs, 3 Users, 10 BusinessTypes, Schemes, Villages & Neighbours
    async with async_session_factory() as session:
        # 1. Orgs
        org1 = Organization(id=1, name="UMED Pune District", type=OrgType.NRLM, district_lgd=490)
        org2 = Organization(id=2, name="CSC Satara", type=OrgType.CSC, district_lgd=491)
        session.add_all([org1, org2])
        await session.flush()

        # 2. Users (PIN '1234' for agent 1, '5678' for agent 2)
        pin_1234 = hash_pin("1234")
        pin_5678 = hash_pin("5678")
        pin_9999 = hash_pin("9999")

        agent1 = User(
            id=1,
            org_id=1,
            role=UserRole.AGENT,
            name="Sunita Patil",
            phone="9876543210",
            pin_hash=pin_1234,
            lang="mr",
        )
        agent2 = User(
            id=2,
            org_id=2,
            role=UserRole.AGENT,
            name="Rahul Shinde",
            phone="9123456789",
            pin_hash=pin_5678,
            lang="mr",
        )
        supervisor = User(
            id=3,
            org_id=1,
            role=UserRole.SUPERVISOR,
            name="Anand Kulkarni",
            phone="9999999999",
            pin_hash=pin_9999,
            lang="mr",
        )
        session.add_all([agent1, agent2, supervisor])

        # 3. Seed business types & schemes
        await seed_business_types(session)
        await seed_schemes(session)

        # 4. Reference village & neighbours
        v1 = Village(
            lgd_code=555001,
            name_en="Shirwal",
            name_mr="शिरवळ",
            subdistrict_lgd=4201,
            subdistrict_name="Haveli",
            district_lgd=490,
            district_name="Pune",
            pop_2011=14250,
        )
        v2 = Village(
            lgd_code=555011,
            name_en="Palashi",
            name_mr="पळशी",
            subdistrict_lgd=4201,
            subdistrict_name="Haveli",
            district_lgd=490,
            district_name="Pune",
            pop_2011=2800,
        )
        v3 = Village(
            lgd_code=555012,
            name_en="Wing",
            name_mr="विंग",
            subdistrict_lgd=4201,
            subdistrict_name="Haveli",
            district_lgd=490,
            district_name="Pune",
            pop_2011=3400,
        )
        session.add_all([v1, v2, v3])
        await session.flush()

        vn1 = VillageNeighbour(lgd_code=555001, neighbour_lgd=555011, dist_km=3.52)
        vn2 = VillageNeighbour(lgd_code=555001, neighbour_lgd=555012, dist_km=4.17)
        session.add_all([vn1, vn2])

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
async def test_auth_login_lifecycle(api_client):
    """Test full login, token generation, rejection on wrong PIN, and /auth/me."""
    client, _ = api_client

    # 1. Invalid PIN -> 401
    bad_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "0000"})
    assert bad_res.status_code == 401
    assert "Invalid phone number or PIN" in bad_res.json()["detail"]

    # 2. Valid Login -> 200 with JWT
    good_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    assert good_res.status_code == 200
    data = good_res.json()
    assert "access_token" in data
    assert data["user"]["name"] == "Sunita Patil"
    assert data["user"]["role"] == "agent"
    token = data["access_token"]

    # 3. /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["id"] == 1
    assert me_res.json()["org_id"] == 1

    # 4. /auth/me without token -> 401
    unauth_res = await client.get("/auth/me")
    assert unauth_res.status_code == 401


@pytest.mark.asyncio
async def test_meta_catalogs(api_client):
    """Test /meta/businesses and /meta/schemes endpoints."""
    client, _ = api_client

    # Businesses
    b_res = await client.get("/meta/businesses")
    assert b_res.status_code == 200
    businesses = b_res.json()
    assert len(businesses) == 10
    codes = {b["code"] for b in businesses}
    assert "dairy" in codes
    assert "kirana" in codes

    # Schemes
    s_res = await client.get("/meta/schemes")
    assert s_res.status_code == 200
    schemes = s_res.json()
    assert len(schemes) >= 10
    sc_codes = {s["code"] for s in schemes}
    assert "PMEGP" in sc_codes
    assert "NSFDC_MFS" in sc_codes


@pytest.mark.asyncio
async def test_beneficiary_dpdp_consent_enforcement(api_client):
    """
    Verify DPDP Act requirement:
    No beneficiary profile can be saved without mandatory consent.
    """
    client, session_factory = api_client

    # Login Agent 1
    login_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Missing consent block -> 422 Unprocessable Entity
    bad_payload = {
        "first_name": "Kavita",
        "gender": "female",
        "age": 28,
        "category": "OBC",
        "income_band": "below_1_lakh",
        "education_band": "class_10_pass",
    }
    res_bad = await client.post("/beneficiaries", json=bad_payload, headers=headers)
    assert res_bad.status_code == 422

    # 2. Valid creation with consent block -> 201 Created
    good_payload = {
        "first_name": "Kavita",
        "gender": "female",
        "age": 28,
        "category": "OBC",
        "category_verified": True,
        "disability_40": False,
        "occupation_flags": [],
        "income_band": "below_1_lakh",
        "education_band": "class_10_pass",
        "shg_member": True,
        "prior_subsidy": "no",
        "credit_default": "no",
        "existing_emi_monthly": 0.0,
        "consent": {
            "notice_version": "v1.0-2026-04",
            "language": "mr",
            "method": "voice",
            "audio_sha256": "abcdef1234567890",
        },
    }
    res_good = await client.post("/beneficiaries", json=good_payload, headers=headers)
    assert res_good.status_code == 201
    b_data = res_good.json()
    assert b_data["id"] > 0
    assert b_data["first_name"] == "Kavita"
    assert b_data["active_consent"] is True

    # 3. Verify AuditLog and ProcessingLog were created in DB
    async with session_factory() as session:
        audit_res = await session.execute(
            select(AuditLog).where(AuditLog.entity == "beneficiaries", AuditLog.action == "CREATE")
        )
        audit_entry = audit_res.scalar_one_or_none()
        assert audit_entry is not None
        assert audit_entry.actor_id == 1

        proc_res = await session.execute(
            select(ProcessingLog).where(ProcessingLog.entity == "beneficiaries")
        )
        proc_entries = proc_res.scalars().all()
        assert len(proc_entries) >= 1

    # 4. List beneficiaries
    list_res = await client.get("/beneficiaries", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
    assert list_res.json()[0]["first_name"] == "Kavita"


@pytest.mark.asyncio
async def test_full_case_lifecycle_and_evaluation(api_client):
    """
    Test end-to-end case journey:
    Create Beneficiary -> Create Case -> Patch Inputs -> Evaluate (Rules + Finance + Viability + Market) -> Update Status.
    """
    client, session_factory = api_client

    # Login Agent 1
    login_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Beneficiary with Consent (SC female for PMEGP / NSFDC eligibility)
    b_payload = {
        "first_name": "Shubhangi",
        "gender": "female",
        "age": 30,
        "category": "SC",
        "category_verified": True,
        "disability_40": False,
        "occupation_flags": ["sanitation_worker"],
        "income_band": "below_1_lakh",
        "education_band": "class_8_pass",
        "shg_member": False,
        "prior_subsidy": "no",
        "credit_default": "no",
        "existing_emi_monthly": 0.0,
        "consent": {
            "notice_version": "v1.0-2026-04",
            "language": "mr",
            "method": "voice",
            "audio_sha256": "feedbeef1234",
        },
    }
    b_res = await client.post("/beneficiaries", json=b_payload, headers=headers)
    b_id = b_res.json()["id"]

    # 2. Create Case (Dairy in Shirwal, margin ₹15,000)
    case_payload = {
        "beneficiary_id": b_id,
        "village_lgd": 555001,  # Shirwal
        "business_code": "dairy",
        "margin_available": 15000.0,
        "target_project_cost": 150000.0,
        "language": "mr",
    }
    c_res = await client.post("/cases", json=case_payload, headers=headers)
    assert c_res.status_code == 201
    c_data = c_res.json()
    c_id = c_data["id"]
    assert c_data["status"] == "draft"

    # 3. Patch Calibration Inputs (2 animals, 18 litres, 2 competitors)
    inputs_payload = {
        "inputs": {
            "animals": 2,
            "daily_production_litres": 18,
            "milk_price_per_litre": 38.0,
            "udhar_pct": 0.20,
            "competitor_count": 2,
        },
    }
    inp_res = await client.patch(f"/cases/{c_id}/inputs", json=inputs_payload, headers=headers)
    assert inp_res.status_code == 200

    # 4. Trigger Multi-Engine Evaluation POST /cases/{id}/evaluate
    eval_res = await client.post(f"/cases/{c_id}/evaluate", headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()

    assert "evaluation_id" in eval_data
    assert "output" in eval_data

    summary = eval_data["output"]["summary"]
    assert summary["business_code"] == "dairy"
    assert summary["village_name"] == "Shirwal"
    assert len(summary["top_packages"]) > 0

    # Top package checks
    top_pkg = summary["top_packages"][0]
    assert "loan_amount" in top_pkg
    assert "monthly_emi" in top_pkg
    assert "subsidy_amount" in top_pkg

    # Viability checks
    assert Decimal(summary["average_dscr"]) >= Decimal("1.0")
    assert "nayak_working_capital" in summary
    assert "udhar_stress" in summary

    # Market checks
    assert summary["market_saturation"] in ["low", "medium", "high"]
    assert int(summary["competitors_reported"]) == 2

    # 5. Check Case Status is now READY
    case_get_res = await client.get(f"/cases/{c_id}", headers=headers)
    assert case_get_res.status_code == 200
    assert case_get_res.json()["status"] == "ready"
    assert case_get_res.json()["latest_evaluation"] is not None

    # 6. Update Status to APPLIED
    stat_res = await client.patch(
        f"/cases/{c_id}/status",
        json={"status": "applied", "status_reason_code": "APPLIED_PSB_ONLINE"},
        headers=headers,
    )
    assert stat_res.status_code == 200
    assert stat_res.json()["new_status"] == "applied"


@pytest.mark.asyncio
async def test_org_isolation_and_rbac(api_client):
    """
    Verify organization boundary isolation:
    Agent 2 (Org 2) CANNOT access or evaluate Case belonging to Agent 1 (Org 1).
    """
    client, _ = api_client

    # Login Agent 1 (Org 1)
    l1 = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token1 = l1.json()["access_token"]
    h1 = {"Authorization": f"Bearer {token1}"}

    # Login Agent 2 (Org 2)
    l2 = await client.post("/auth/login", json={"phone": "9123456789", "pin": "5678"})
    token2 = l2.json()["access_token"]
    h2 = {"Authorization": f"Bearer {token2}"}

    # Agent 1 creates beneficiary and case in Org 1
    b_res = await client.post(
        "/beneficiaries",
        json={
            "first_name": "Sunil",
            "gender": "male",
            "age": 35,
            "category": "General",
            "consent": {"notice_version": "v1.0-2026-04", "method": "tap"},
        },
        headers=h1,
    )
    b_id = b_res.json()["id"]

    c_res = await client.post(
        "/cases",
        json={
            "beneficiary_id": b_id,
            "village_lgd": 555001,
            "business_code": "kirana",
            "margin_available": 20000.0,
        },
        headers=h1,
    )
    case_id = c_res.json()["id"]

    # Agent 2 attempts to GET Case -> 404 (isolated)
    bad_get = await client.get(f"/cases/{case_id}", headers=h2)
    assert bad_get.status_code == 404

    # Agent 2 attempts to evaluate Case -> 404 (isolated)
    bad_eval = await client.post(f"/cases/{case_id}/evaluate", headers=h2)
    assert bad_eval.status_code == 404


@pytest.mark.asyncio
async def test_dashboard_summary(api_client):
    """Test supervisor summary dashboard."""
    client, _ = api_client

    login_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = await client.get("/dashboard/summary", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["org_id"] == 1
    assert "total_cases" in data
    assert "cases_by_status" in data
    assert "cases_by_business" in data
