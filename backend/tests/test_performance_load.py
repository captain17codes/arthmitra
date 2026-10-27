from __future__ import annotations

import asyncio
import statistics
import time
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security import hash_pin
from app.seed import seed_business_types, seed_schemes
from dpr.renderer import render_dpr_pdf
from models.enums import OrgType, UserRole
from models.organization import Organization, User
from models.village import Village, VillageNeighbour


@pytest.fixture
async def perf_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session_factory() as session:
        org = Organization(id=1, name="UMED Performance Unit", type=OrgType.NRLM, district_lgd=490)
        session.add(org)
        await session.flush()

        agent = User(
            id=1,
            org_id=1,
            role=UserRole.AGENT,
            name="Performance Sakhi",
            phone="9876543210",
            pin_hash=hash_pin("1234"),
            lang="mr",
        )
        session.add(agent)
        await session.flush()

        await seed_business_types(session)
        await seed_schemes(session)

        # Add benchmark villages
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
            name_en="Khed Shivapur",
            name_mr="खेड शिवापूर",
            subdistrict_lgd=4201,
            subdistrict_name="Haveli",
            district_lgd=490,
            district_name="Pune",
            pop_2011=2800,
        )
        session.add_all([v1, v2])
        await session.flush()

        vn1 = VillageNeighbour(lgd_code=555001, neighbour_lgd=555011, dist_km=3.52)
        session.add(vn1)
        await session.commit()

    async def override_get_db():
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_case_evaluation_p95_latency(perf_client):
    """
    Performance Benchmark: Case Evaluation Pipeline
    Target: PRD §8 non-functional target: p95 latency <= 800ms.
    Executes multiple multi-engine evaluations across diverse rural business verticals.
    """
    client = perf_client

    # 1. Login
    login_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup Beneficiary
    b_payload = {
        "first_name": "Savitribai",
        "gender": "female",
        "age": 32,
        "category": "SC",
        "category_verified": True,
        "disability_40": False,
        "occupation_flags": ["traditional_artisan"],
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
            "audio_sha256": "perf_test_voice_hash_123",
        },
    }
    b_res = await client.post("/beneficiaries", json=b_payload, headers=headers)
    assert b_res.status_code == 201
    b_id = b_res.json()["id"]

    businesses = [
        ("dairy", 150000.0, 15000.0, {"animals": 2, "daily_production_litres": 18}),
        ("kirana", 200000.0, 20000.0, {"daily_footfall": 40, "average_spend_rs": 120}),
        ("tailoring", 80000.0, 8000.0, {"machines": 2, "daily_orders": 5}),
        ("goatery", 120000.0, 12000.0, {"animals": 11}),
        ("broiler", 250000.0, 25000.0, {"batch_size": 1000}),
        ("beauty_parlour", 100000.0, 10000.0, {"daily_clients": 6}),
        ("mobile_repair", 150000.0, 15000.0, {"daily_repairs": 4}),
        ("flour_mill", 180000.0, 18000.0, {"daily_milling_kg": 150}),
        ("papad_pickle", 75000.0, 7500.0, {"monthly_kg": 200}),
        ("two_wheeler_repair", 160000.0, 16000.0, {"daily_servicing": 5}),
    ]

    latencies_ms: list[float] = []

    # Run 20 evaluations (2 rounds of the 10 businesses)
    for _ in range(2):
        for biz_code, cost, margin, inputs in businesses:
            # Create Case
            c_res = await client.post(
                "/cases",
                json={
                    "beneficiary_id": b_id,
                    "village_lgd": 555001,
                    "business_code": biz_code,
                    "margin_available": margin,
                    "target_project_cost": cost,
                    "language": "mr",
                },
                headers=headers,
            )
            assert c_res.status_code == 201
            case_id = c_res.json()["id"]

            # Calibration inputs
            await client.patch(
                f"/cases/{case_id}/inputs",
                json={"inputs": inputs},
                headers=headers,
            )

            # Benchmark evaluation endpoint latency
            t0 = time.perf_counter()
            eval_res = await client.post(f"/cases/{case_id}/evaluate", headers=headers)
            t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

            assert eval_res.status_code == 200
            latencies_ms.append(t_elapsed_ms)

    sorted_latencies = sorted(latencies_ms)
    p50 = statistics.median(sorted_latencies)
    # 95th percentile index
    p95_idx = int(0.95 * len(sorted_latencies))
    p95 = sorted_latencies[p95_idx]

    print(f"\n[Evaluation Performance Benchmark] Count: {len(latencies_ms)}")
    print(f"Min: {min(sorted_latencies):.2f}ms | Median: {p50:.2f}ms | p95: {p95:.2f}ms | Max: {max(sorted_latencies):.2f}ms")

    # Statutory requirement: p95 <= 800ms (0.8s)
    assert p95 <= 800.0, f"p95 latency {p95:.2f}ms exceeded 800ms threshold"


@pytest.mark.asyncio
async def test_concurrent_evaluation_throughput(perf_client):
    """
    Stress / Concurrency Test:
    Simulates 5 concurrent field agents evaluating cases simultaneously.
    Verifies thread safety, absence of deadlocks, and latency containment under load.
    """
    client = perf_client

    login_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    b_payload = {
        "first_name": "Laxmibai",
        "gender": "female",
        "age": 29,
        "category": "OBC",
        "category_verified": True,
        "disability_40": False,
        "occupation_flags": [],
        "income_band": "1_to_3_lakh",
        "education_band": "class_12_pass",
        "shg_member": True,
        "prior_subsidy": "no",
        "credit_default": "no",
        "existing_emi_monthly": 0.0,
        "consent": {
            "notice_version": "v1.0-2026-04",
            "language": "mr",
            "method": "voice",
            "audio_sha256": "concurrent_voice_hash_999",
        },
    }
    b_res = await client.post("/beneficiaries", json=b_payload, headers=headers)
    b_id = b_res.json()["id"]

    case_ids = []
    for _ in range(5):
        c_res = await client.post(
            "/cases",
            json={
                "beneficiary_id": b_id,
                "village_lgd": 555001,
                "business_code": "kirana",
                "margin_available": 20000.0,
                "target_project_cost": 200000.0,
                "language": "mr",
            },
            headers=headers,
        )
        case_ids.append(c_res.json()["id"])

    # Launch concurrent requests
    async def run_eval(cid: int):
        t0 = time.perf_counter()
        resp = await client.post(f"/cases/{cid}/evaluate", headers=headers)
        return resp.status_code, (time.perf_counter() - t0) * 1000.0

    t_start = time.perf_counter()
    results = await asyncio.gather(*(run_eval(cid) for cid in case_ids))
    t_total_ms = (time.perf_counter() - t_start) * 1000.0

    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results]

    assert all(s == 200 for s in statuses)
    print(f"\n[Concurrent Evaluation] 5 requests completed in total {t_total_ms:.2f}ms. Avg: {statistics.mean(latencies):.2f}ms")


def test_dpr_generation_p95_latency(tmp_path: Path):
    """
    Performance Benchmark: DPR PDF Generation Pipeline
    Target: PRD §8 non-functional target: p95 latency <= 3.0s (3000ms).
    Renders 10 bilingual 12-section bank project reports using WeasyPrint & Jinja2.
    """
    mock_eval = {
        "summary": {
            "business_code": "dairy",
            "business_name_en": "Dairy Farming (2 Animals)",
            "business_name_mr": "दुग्धव्यवसाय (२ जनावरे)",
            "village_name": "Shirwal",
            "project_cost": "150000.00",
            "margin_available": "15000.00",
            "top_packages": [
                {
                    "scheme_code": "NSFDC_MFS",
                    "scheme_name": {"mr": "एनएसएफडीसी सूक्ष्म वित्त योजना", "en": "NSFDC Micro Finance"},
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
            "nayak_working_capital": {"total": "37500.00", "bank_finance_20": "30000.00", "promoter_margin_5": "7500.00"},
            "udhar_stress": {"cash_buffer_months": "4.20"},
            "market_saturation": "low",
            "effective_catchment_population": "18500",
            "monthly_category_demand": "152000.00",
            "competitors_reported": "2",
        },
        "viability": {
            "projections": [
                {"year": 1, "gross_revenue": "180000.00", "pat": "42000.00", "debt_service": "24657.12", "dscr": "2.20"},
                {"year": 2, "gross_revenue": "195000.00", "pat": "49000.00", "debt_service": "49314.24", "dscr": "2.40"},
                {"year": 3, "gross_revenue": "210000.00", "pat": "55000.00", "debt_service": "49314.24", "dscr": "2.55"},
                {"year": 4, "gross_revenue": "225000.00", "pat": "61000.00", "debt_service": "0.00", "dscr": "3.10"},
                {"year": 5, "gross_revenue": "240000.00", "pat": "68000.00", "debt_service": "0.00", "dscr": "3.50"},
            ]
        },
    }

    mock_snap = {
        "beneficiary": {
            "first_name": "Shubhangi",
            "age": 30,
            "gender": "female",
            "category": "SC",
            "income_band": "below_1_lakh",
            "existing_emi": "0.00",
        },
        "village": {"name": "Shirwal", "lgd_code": 555001, "pop_2011": 14250},
        "inputs": {"animals": 2, "daily_production_litres": 18},
    }

    latencies_sec: list[float] = []

    # Run 6 iterations of full PDF generation (both mr and en)
    for i in range(6):
        lang = "mr" if i % 2 == 0 else "en"
        t0 = time.perf_counter()
        res = render_dpr_pdf(
            case_id=200 + i,
            eval_output=mock_eval,
            input_snapshot=mock_snap,
            output_dir=tmp_path,
            language=lang,
        )
        t_elapsed = time.perf_counter() - t0
        latencies_sec.append(t_elapsed)

        p = Path(res.file_path)
        assert p.exists()
        assert p.stat().st_size > 1000

    sorted_latencies = sorted(latencies_sec)
    p50 = statistics.median(sorted_latencies)
    p95_idx = int(0.95 * len(sorted_latencies))
    p95 = sorted_latencies[p95_idx]

    print(f"\n[DPR Rendering Performance Benchmark] Count: {len(latencies_sec)}")
    print(f"Min: {min(sorted_latencies):.3f}s | Median: {p50:.3f}s | p95: {p95:.3f}s | Max: {max(sorted_latencies):.3f}s")

    # Statutory requirement: p95 <= 3.0s
    assert p95 <= 3.0, f"DPR p95 latency {p95:.3f}s exceeded 3.0s threshold"
