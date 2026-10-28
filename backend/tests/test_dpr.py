from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.security import hash_pin
from app.seed import seed_business_types, seed_schemes
from dpr.builder import build_dpr_sections
from dpr.renderer import render_dpr_pdf
from models.enums import OrgType, UserRole
from models.organization import Organization, User
from models.village import Village


def test_dpr_builder_all_twelve_sections():
    """Verify build_dpr_sections produces all 12 bank-required sections per TECH_SPEC §7.2."""
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
                    "scheme_name": {"mr": "एनएसएफडीसी सूक्ष्म वित्त योजना"},
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
            ]
        },
    }
    mock_snap = {
        "beneficiary": {"first_name": "Shubhangi", "age": 30, "gender": "female", "category": "SC", "income_band": "below_1_lakh", "existing_emi": "0.00"},
        "village": {"name": "Shirwal", "lgd_code": 555001, "pop_2011": 14250},
        "inputs": {"animals": 2, "daily_production_litres": 18},
    }

    sections = build_dpr_sections(mock_eval, mock_snap, language="mr")
    assert len(sections) == 12

    # Check that all 12 section numbers exist from 1 to 12
    sec_nums = [s.section_number for s in sections]
    assert sec_nums == list(range(1, 13))

    # Verify both Marathi and English titles & contents exist
    for s in sections:
        assert s.title_mr != ""
        assert s.title_en != ""
        assert s.content_mr != ""
        assert s.content_en != ""


def test_dpr_pdf_rendering_and_sha256(tmp_path):
    """Verify render_dpr_pdf produces valid PDF with verifiable SHA-256 digest in Marathi and English."""
    mock_eval = {
        "summary": {
            "business_code": "kirana",
            "business_name_en": "Kirana Store",
            "business_name_mr": "किराणा दुकान",
            "village_name": "Khed Shivapur",
            "project_cost": "200000.00",
            "margin_available": "20000.00",
            "top_packages": [
                {
                    "scheme_code": "PMEGP",
                    "scheme_name": {"mr": "पंतप्रधान रोजगार निर्मिती कार्यक्रम (PMEGP)"},
                    "loan_amount": "190000.00",
                    "subsidy_amount": "70000.00",
                    "own_margin_required": "10000.00",
                    "annual_rate_pct": "10.00",
                    "tenure_months": 84,
                    "moratorium_months": 6,
                    "monthly_emi": "3200.00",
                    "total_repayment": "268800.00",
                }
            ],
            "average_dscr": "1.85",
            "breakeven_capacity_pct": "42.0",
            "nayak_working_capital": {"total": "50000.00"},
            "udhar_stress": {"cash_buffer_months": "3.5"},
            "market_saturation": "medium",
            "effective_catchment_population": "12000",
            "monthly_category_demand": "240000.00",
            "competitors_reported": "3",
        },
        "viability": {"projections": []},
    }
    mock_snap = {
        "beneficiary": {"first_name": "Ramesh", "age": 35, "gender": "male", "category": "OBC", "income_band": "1_to_3_lakh"},
        "village": {"name": "Khed Shivapur", "lgd_code": 555002},
        "inputs": {},
    }

    # 1. Render Marathi copy
    res_mr = render_dpr_pdf(case_id=101, eval_output=mock_eval, input_snapshot=mock_snap, output_dir=tmp_path, language="mr")
    p_mr = Path(res_mr.file_path)
    assert p_mr.exists()
    assert p_mr.stat().st_size > 1000
    with open(p_mr, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"
        f.seek(0)
        assert hashlib.sha256(f.read()).hexdigest() == res_mr.file_sha256

    # 2. Render English copy
    res_en = render_dpr_pdf(case_id=101, eval_output=mock_eval, input_snapshot=mock_snap, output_dir=tmp_path, language="en")
    p_en = Path(res_en.file_path)
    assert p_en.exists()
    assert p_en.stat().st_size > 1000
    with open(p_en, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"


@pytest.fixture
async def dpr_client():
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
async def test_dpr_api_workflow(dpr_client):
    """Test full DPR generation, listing, and download workflow via API."""
    client, _ = dpr_client

    # 1. Login
    l_res = await client.post("/auth/login", json={"phone": "9876543210", "pin": "1234"})
    token = l_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Beneficiary + Case + Evaluate
    b_res = await client.post(
        "/beneficiaries",
        json={
            "first_name": "Pooja",
            "gender": "female",
            "age": 29,
            "category": "SC",
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

    # 3. Generate DPR
    dpr_res = await client.post(f"/evaluations/{eval_id}/dpr?language=mr", headers=headers)
    assert dpr_res.status_code == 200
    dpr_data = dpr_res.json()
    assert "dpr_id" in dpr_data
    assert "file_sha256" in dpr_data
    assert dpr_data["language"] == "mr"
    doc_id = dpr_data["dpr_id"]

    # 4. List DPRs (should return both Marathi and English copies)
    list_res = await client.get(f"/evaluations/{eval_id}/dpr", headers=headers)
    assert list_res.status_code == 200
    docs = list_res.json()
    assert len(docs) >= 2
    langs = {d["language"] for d in docs}
    assert "mr" in langs
    assert "en" in langs

    # 5. Download DPR binary
    # Download requires auth (DPRs contain personal data)
    unauth_res = await client.get(f"/dpr/{doc_id}/download")
    assert unauth_res.status_code == 401
    dl_res = await client.get(f"/dpr/{doc_id}/download", headers=headers)
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert dl_res.content[:4] == b"%PDF"


def test_dpr_builder_uses_only_computed_values():
    """Regression: no invented cost split, real promoter name, honest DSCR conclusion, scheme documents."""
    from dpr.builder import build_dpr_sections, format_currency_inr
    from dpr.renderer import _init_pdf_fonts, _markup

    assert format_currency_inr(2948400) == "₹29,48,400.00"
    out = {
        "summary": {
            "project_cost": "200000",
            "average_dscr": "0.90",
            "dscr_passed": False,
            "top_packages": [{
                "scheme_code": "PMEGP", "scheme_name": {"en": "PMEGP", "mr": "पीएमईजीपी"},
                "documents": ["caste_certificate"], "apply_at": "kviconline.gov.in",
                "source_url": "https://kviconline.gov.in", "subsidy_treatment": "fdr_3yr",
            }],
        },
        "viability": {"dscr_target": "1.25", "inputs_used": {"daily_customers": "local"}, "warnings": ["W1"]},
    }
    snap = {"inputs": {"daily_customers": "40"}, "beneficiary": {}, "village": {}}
    bench = {"capex": {"shelves": {"value": 35000, "confidence": "estimate"}},
             "revenue_parameters": {"daily_customers": {"value": 65, "unit": "customers/day"}}}
    secs = {s.section_number: s for s in build_dpr_sections(out, snap, "en", promoter_name="Asha", benchmark=bench)}
    assert "Promoter Name: Asha" in secs[1].content_en
    assert "shelves" in secs[4].content_en and "₹1,65,000.00" in secs[4].content_en  # balance, not a 90/5/5 split
    assert "Contingency" not in secs[4].content_en
    assert "entered locally" in secs[6].content_en
    assert "below the bank threshold" in secs[8].content_en
    assert "W1" in secs[10].content_en
    assert "caste certificate" in secs[11].content_en and "kviconline.gov.in" in secs[11].content_en

    assert _init_pdf_fonts() is True
    m = _markup("गाव (Village) A&B", True)
    assert "&amp;" in m and '<font name="NotoLatin">(Village) A&amp;B</font>' in m
