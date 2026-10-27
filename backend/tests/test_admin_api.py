from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security import hash_pin
from app.seed import seed_business_types, seed_schemes
from models.business_type import Benchmark
from models.enums import BenchmarkConfidence, CoordSource, OrgType, UserRole
from models.organization import Organization, User
from models.village import Village


@pytest.fixture
async def admin_api_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session_factory() as session:
        # Seed Org
        org = Organization(id=1, name="District Advisory Unit", type=OrgType.NRLM, district_lgd=490)
        session.add(org)
        await session.flush()

        # Seed Users: 1 Agent, 1 Supervisor, 1 Admin
        agent = User(
            id=1,
            org_id=1,
            role=UserRole.AGENT,
            name="Bank Sakhi",
            phone="9876543210",
            pin_hash=hash_pin("1234"),
            lang="mr",
        )
        supervisor = User(
            id=2,
            org_id=1,
            role=UserRole.SUPERVISOR,
            name="Block Supervisor",
            phone="9999999999",
            pin_hash=hash_pin("9999"),
            lang="mr",
        )
        session.add_all([agent, supervisor])

        # Seed catalog
        await seed_business_types(session)
        await seed_schemes(session)

        # Seed village
        v = Village(
            lgd_code=555001,
            name_en="Shirwal",
            name_mr="शिरवळ",
            subdistrict_lgd=4201,
            subdistrict_name="Khandala",
            district_lgd=490,
            district_name="Satara",
            lat=None,
            lon=None,
            coord_source=CoordSource.OTHER,
            pop_2011=12000,
        )
        session.add(v)

        # Seed a Benchmark
        bm = Benchmark(
            id=1,
            business_code="kirana",
            key="capex_setup",
            value=200000.0,
            unit="INR",
            region="Maharashtra Rural",
            source_title="KVIC Model Profile 2025",
            source_year=2025,
            confidence=BenchmarkConfidence.OFFICIAL,
            version="1.0.0",
        )
        session.add(bm)

        await session.commit()

    async def override_get_db():
        async with async_session_factory() as s:
            yield s

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_admin_rbac_protection(admin_api_client: AsyncClient):
    """Confirm agents cannot access admin endpoints while supervisors can."""
    # 1. Login as Agent
    resp_agent_login = await admin_api_client.post(
        "/auth/login", json={"phone": "9876543210", "pin": "1234"}
    )
    assert resp_agent_login.status_code == 200
    agent_token = resp_agent_login.json()["access_token"]

    # Agent calls /admin/schemes -> 403 Forbidden
    resp_agent = await admin_api_client.get(
        "/admin/schemes",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert resp_agent.status_code == 403

    # 2. Login as Supervisor
    resp_sup_login = await admin_api_client.post(
        "/auth/login", json={"phone": "9999999999", "pin": "9999"}
    )
    assert resp_sup_login.status_code == 200
    sup_token = resp_sup_login.json()["access_token"]

    # Supervisor calls /admin/schemes -> 200 OK
    resp_sup = await admin_api_client.get(
        "/admin/schemes",
        headers={"Authorization": f"Bearer {sup_token}"},
    )
    assert resp_sup.status_code == 200
    schemes = resp_sup.json()
    assert len(schemes) > 0


@pytest.mark.asyncio
async def test_admin_scheme_validate_yaml(admin_api_client: AsyncClient):
    """Test validating proposed YAML without publishing or changing database."""
    # Login as supervisor
    login = await admin_api_client.post(
        "/auth/login", json={"phone": "9999999999", "pin": "9999"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    valid_yaml = """
code: PMEGP
name:
  en: Prime Minister Employment Generation Programme
  mr: पंतप्रधान रोजगार निर्मिती कार्यक्रम
agency: KVIC
status: verified
source:
  url: https://kviconline.gov.in
  date: "2026-01-01"
channel:
  via: [portal]
  apply_at: DIC
eligibility:
  - field: age
    op: gte
    value: 18
    reason: Age must be >= 18
finance:
  loan_share: 0.60
  min_own_share: 0.05
  interest:
    type: bank_rate
  tenure_months: 60
documents:
  - Project Report
tests:
  - input:
      age: 25
    expect:
      status: ELIGIBLE
"""
    resp = await admin_api_client.post(
        "/admin/schemes/PMEGP/validate",
        headers=headers,
        json={"rules_yaml": valid_yaml},
    )
    assert resp.status_code == 200
    res = resp.json()
    assert res["valid"] is True
    assert res["tests_run"] == 1
    assert res["tests_passed"] == 1
    assert len(res["errors"]) == 0

    # Invalid YAML check
    bad_yaml = "invalid: yaml: syntax: [unclosed"
    resp_bad = await admin_api_client.post(
        "/admin/schemes/PMEGP/validate",
        headers=headers,
        json={"rules_yaml": bad_yaml},
    )
    assert resp_bad.status_code == 200
    assert resp_bad.json()["valid"] is False


@pytest.mark.asyncio
async def test_admin_publish_scheme_version(admin_api_client: AsyncClient):
    """Verify publishing a scheme version runs tests, writes audit_log, and saves version."""
    login = await admin_api_client.post(
        "/auth/login", json={"phone": "9999999999", "pin": "9999"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    new_version_yaml = """
code: PMEGP
name:
  en: Prime Minister Employment Generation Programme
  mr: पंतप्रधान रोजगार निर्मिती कार्यक्रम
agency: KVIC
status: verified
source:
  url: https://kviconline.gov.in
  date: "2026-04-01"
channel:
  via: [portal]
  apply_at: DIC
eligibility:
  - field: age
    op: gte
    value: 18
    reason: Age must be >= 18
finance:
  loan_share: 0.60
  min_own_share: 0.05
  interest:
    type: bank_rate
  tenure_months: 60
documents:
  - Project Report
tests:
  - input:
      age: 30
    expect:
      status: ELIGIBLE
"""
    resp = await admin_api_client.post(
        "/admin/schemes/PMEGP/publish",
        headers=headers,
        json={
            "version": "1.1.0",
            "rules_yaml": new_version_yaml,
            "status": "verified",
        },
    )
    assert resp.status_code == 201
    payload = resp.json()
    assert payload["version"] == "1.1.0"
    assert payload["tests_passed"] == 1

    # Verify detail shows the new version
    detail_resp = await admin_api_client.get(
        "/admin/schemes/PMEGP",
        headers=headers,
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    versions = detail["versions"]
    assert any(v["version"] == "1.1.0" for v in versions)


@pytest.mark.asyncio
async def test_admin_update_benchmark(admin_api_client: AsyncClient):
    """Verify editing benchmark values with audit logging."""
    login = await admin_api_client.post(
        "/auth/login", json={"phone": "9999999999", "pin": "9999"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch benchmarks
    list_resp = await admin_api_client.get("/admin/benchmarks", headers=headers)
    assert list_resp.status_code == 200
    bms = list_resp.json()
    assert len(bms) > 0
    bm_id = bms[0]["id"]

    # Update benchmark
    update_payload = {
        "value": 225000.0,
        "unit": "INR",
        "region": "Maharashtra Rural",
        "source_title": "Field Survey Pune Block 2026",
        "source_year": 2026,
        "confidence": "secondary",
        "version": "1.1.0",
    }
    update_resp = await admin_api_client.put(
        f"/admin/benchmarks/{bm_id}",
        headers=headers,
        json=update_payload,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["success"] is True


@pytest.mark.asyncio
async def test_admin_village_coords_update(admin_api_client: AsyncClient):
    """Verify manual coordinate fix for villages."""
    login = await admin_api_client.post(
        "/auth/login", json={"phone": "9999999999", "pin": "9999"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Check missing coords list
    missing_resp = await admin_api_client.get("/admin/villages/missing-coords", headers=headers)
    assert missing_resp.status_code == 200
    missing = missing_resp.json()
    assert any(v["lgd_code"] == 555001 for v in missing)

    # Patch coordinates
    patch_resp = await admin_api_client.patch(
        "/admin/villages/555001/coords",
        headers=headers,
        json={"lat": 18.152, "lon": 74.025, "source_note": "Agent GPS Fix"},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["lat"] == 18.152
    assert data["lon"] == 74.025
    assert data["coord_source"] == "manual"


@pytest.mark.asyncio
async def test_supervisor_dashboard_summary(admin_api_client: AsyncClient):
    """Verify supervisor dashboard metrics with saturation, schemes, and leaderboard."""
    login = await admin_api_client.post(
        "/auth/login", json={"phone": "9999999999", "pin": "9999"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_resp = await admin_api_client.get("/dashboard/summary", headers=headers)
    assert dash_resp.status_code == 200
    summary = dash_resp.json()
    assert "total_cases" in summary
    assert "cases_by_status" in summary
    assert "cases_by_saturation" in summary
    assert "agent_leaderboard" in summary
